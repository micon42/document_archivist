import argparse
import datetime
import json
import logging
import mariadb
import os
import re
import shutil
import sys


class document_manager:
    def __init__(self):
        try:
            conn = mariadb.connect(
                user="example",
                password="example",
                host="127.0.0.1",
                port=3306,
                database="scanned_doc_db",
            )
            conn.autocommit = True
        except mariadb.Error as e:
            logging.error(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)

        # Get Cursor
        self._cur = conn.cursor()

    def write_doc_data(self, input_dir, input_name, archive_path):
        work_files = self._get_files(input_dir, input_name)

        for f in work_files:
            if -1 != f.find(".pdf"):
                pdf_path = f
            if -1 != f.find("1-to-") and -1 == f.find("_summary"):
                text_path = f
            if -1 != f.find("_summary"):
                summary_path = f

        with open(text_path, "r") as read_file:
            doc_data = json.load(read_file)

        doc_data = doc_data["responses"]
        doc_data = doc_data[0]
        doc_data = doc_data["fullTextAnnotation"]
        ocr_text = doc_data["text"]

        with open(summary_path, "r") as read_file:
            doc_summary = json.load(read_file)

        key_word_dict = {}
        key_words_list = []
        for key_word in doc_summary["keywords"]:
            key_word = key_word.lower()
            key_word = key_word.replace("ä", "ae")
            key_word = key_word.replace("ö", "oe")
            key_word = key_word.replace("ü", "ue")
            key_word = re.sub(r"[^a-zA-Z0-9]", "_", key_word)
            key_words_list.append(key_word)
            try:
                self._cur.execute(
                    "SELECT TagId,Name FROM Tags WHERE Name=?",
                    (key_word,),
                )
            except mariadb.Error as e:
                logging.error(f"Error: {e}")
            key_exists = False
            for tag_id, name in self._cur:
                key_word_dict[name] = tag_id
                if key_word == name:
                    key_exists = True

            if not key_exists:
                try:
                    self._cur.execute("INSERT INTO Tags (Name) VALUES (?)", (key_word,))
                    key_word_dict[key_word] = self._cur.lastrowid
                except mariadb.Error as e:
                    logging.error(f"Error: {e}")
                    sys.exit(1)

        datetime_now = datetime.datetime.now()
        doc_date = datetime_now.strftime("%Y-%m-%d")

        # move documents to archive
        doc_name_date = datetime_now.strftime("%Y-%m-%d_%H%M%S")
        new_doc_name = "_".join(key_words_list)
        new_doc_name += "_" + doc_name_date

        archive_path = os.path.join(archive_path, datetime_now.strftime("%Y"))
        new_doc_name = os.path.join(archive_path, new_doc_name)

        new_pdf_path = new_doc_name + ".pdf"
        new_ocr_path = new_doc_name + "_ocr_0.json"
        new_summary_path = new_doc_name + "_summary.json"

        shutil.move(pdf_path, new_pdf_path)
        shutil.move(text_path, new_ocr_path)
        shutil.move(summary_path, new_summary_path)

        # rename and move further scanned pages
        work_files = self._get_files(input_dir, input_name)
        for idx, f in enumerate(work_files):
            new_file_path = new_doc_name + f"_ocr_{idx+1}.json"
            shutil.move(f, new_file_path)

        doc_path, doc_name = os.path.split(new_pdf_path)

        try:
            self._cur.execute(
                "INSERT INTO Documents (Name, Path, Date, Summary, OCR) VALUES (?, ?, ?, ?, ?)",
                (doc_name, doc_path, doc_date, doc_summary["summary"], ocr_text),
            )
            doc_id = self._cur.lastrowid
        except mariadb.Error as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

        for _, tag_id in key_word_dict.items():
            try:
                self._cur.execute(
                    "INSERT INTO DocTag (DocId, TagId) VALUES (?, ?)",
                    (doc_id, tag_id),
                )
            except mariadb.Error as e:
                logging.error(f"Error: {e}")
                sys.exit(1)

    @staticmethod
    def _get_files(input_dir, input_name):
        all_files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]
        work_files = [
            os.path.join(args.input_dir, f)
            for f in all_files
            if -1 != f.find(input_name)
        ]
        return work_files


if __name__ == "__main__":
    logging.basicConfig(
        filename="archive_documents.log",
        format="%(asctime)s%(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        encoding="utf-8",
        level=logging.DEBUG,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Path to working dir")
    parser.add_argument("input_name", help="Base name of input document")
    parser.add_argument("archive_path", help="Archive path for the documents")
    args = parser.parse_args()

    logging.debug(f"add_document_to_database.py called for {args.input_name}")

    dbm = document_manager()
    dbm.write_doc_data(
        args.input_dir,
        args.input_name,
        args.archive_path,
    )

    with open("/home/example/archive_documents/data_added_flag", "w") as out_file:
        out_file.write(args.input_name)

    logging.debug("add_document_to_database.py successfully finished")
