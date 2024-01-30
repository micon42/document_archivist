import argparse
import logging
import os
import sys


def async_detect_document(gcs_source_uri, gcs_destination_uri, out_file_list):
    """OCR with PDF/TIFF as source files on GCS"""
    """Copied from https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/vision/snippets/detect/detect.py (January 2024)"""
    """Modified to meet the requirements of this project"""

    import json
    import re
    from google.cloud import vision
    from google.cloud import storage

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = "application/pdf"

    # How many pages should be grouped into each json output file.
    batch_size = 3

    client = vision.ImageAnnotatorClient()

    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size
    )

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )

    operation = client.async_batch_annotate_files(requests=[async_request])

    # print("Waiting for the operation to finish.")
    operation.result(timeout=420)

    # Once the request has completed and the output has been
    # written to GCS, we can list all the output files.
    storage_client = storage.Client()

    match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.get_bucket(bucket_name)

    # Write first output file to list
    blob_list = [
        blob
        for blob in list(bucket.list_blobs(prefix=prefix))
        if not blob.name.endswith("/")
    ]
    for blob in blob_list:
        blob_name = blob.name
        # if -1 != blob_name.find("("):
        #     blob_name = blob_name[: blob_name.find("(")]
        with open(out_file_list, "w") as out_file:
            out_file.write(blob_name)
        break

    if not blob_list:
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(
        filename="archive_documents.log",
        format="%(asctime)s%(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        encoding="utf-8",
        level=logging.DEBUG,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input path")
    parser.add_argument("out_file_list", help="List of result files")
    args = parser.parse_args()

    logging.debug(f"pdf_to_text.py called for {args.input}")

    out_name, _ = os.path.splitext(args.input)
    out_name += "_"

    async_detect_document(args.input, out_name, args.out_file_list)

    logging.debug("pdf_to_text.py successfully finished")
