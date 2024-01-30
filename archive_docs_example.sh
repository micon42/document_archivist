#!/bin/bash

source /home/example/archive_documents/export_keys.sh
source ~/anaconda3/etc/profile.d/conda.sh
conda activate google_cli

cd /home/example/archive_documents

source cleanup_log.sh

onedrive --synchronize --single-directory 'Dokumente/Scans'
if [ $? -ne 0 ]; then 
  logger '[archive_docs] Onedrive Dokumente/Scans sync failed'
  exit 1
fi

onedrive_dir='/home/example/OneDrive/Dokumente/Scans'
if [ -z "$(ls -A $onedrive_dir)" ]; then
   exit 0
fi

for entry in $onedrive_dir/*.pdf
do
  filename=$(basename -- "$entry")
  file_base_name="${filename%.*}"
  
  /home/example/google-cloud-sdk/bin/gcloud storage cp $entry gs://my-example-bucket
  if [ $? -ne 0 ]; then 
    logger '[archive_docs] gcloud copy of $entry to gs://my-example-bucket failed'
    exit 1
  fi

  python pdf_to_text.py gs://my-example-bucket/$filename /home/example/archive_documents/current_work_file.txt
  if [ $? -ne 0 ]; then
    logger '[archive_docs] pdf_to_text failed'
    exit 1
  fi

  /home/example/google-cloud-sdk/bin/gcloud storage cp gs://my-example-bucket/* /home/example/archive_documents/work/
  if [ $? -ne 0 ]; then 
    logger '[archive_docs] gcloud copy from gs://my-example-bucket failed'
    exit 1
  fi

  /home/example/google-cloud-sdk/bin/gcloud storage rm gs://my-example-bucket/*
  if [ $? -ne 0 ]; then 
    logger '[archive_docs] gcloud remove files from gs://my-example-bucket failed'
  fi

  python get_summary_from_text.py /home/example/archive_documents/work/ /home/example/archive_documents/current_work_file.txt
  if [ $? -ne 0 ]; then 
    logger '[archive_docs] get_summary_from_text failed'
    exit 1
  fi

  python add_document_to_database.py /home/example/archive_documents/work/ $file_base_name /home/example/OneDrive/Documents/documents_archive
  if [ $? -ne 0 ]; then 
    logger '[archive_docs] add_document_to_database failed'
    exit 1
  fi

done

rm -rf $onedrive_dir/*
if [ $? -ne 0 ]; then 
  logger '[archive_docs] Removal of files from Dokumente/Scans failed'
fi

onedrive --synchronize --single-directory 'Dokumente/Scans'
if [ $? -ne 0 ]; then 
  logger '[archive_docs] Onedrive Dokumente/Scans second sync failed'
fi

FILE=/home/example/archive_documents/data_added_flag
if [[ -f "$FILE" ]]; then
  rm -f $FILE
  BACKUP_DATE=$(date +'%Y-%m-%d_%H%M%S')
  TARGET_DIR=/mnt/example_backup/${BACKUP_DATE}
  mariabackup --backup --databases="scanned_doc_db" --target-dir=${TARGET_DIR} --user=example --password=example
  if [ $? -eq 0 ]; then 
    tar -czf /home/example/OneDrive/documents_archive/example_backup/${BACKUP_DATE}.tar.gz ${TARGET_DIR}/
    if [ $? -ne 0 ]; then 
      logger '[archive_docs] tar of mariadb backup $BACKUP_DATE failed'
    fi
  else
    logger '[archive_docs] mariabackup failed'
  fi
fi

onedrive --synchronize --single-directory 'Documents/documents_archive'
if [ $? -ne 0 ]; then 
  logger '[archive_docs] Onedrive Documents/documents_archive sync failed'
fi
