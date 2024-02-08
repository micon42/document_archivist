import argparse
import json
import logging
import os
import sys
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_response(prompt):
    gpt_response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4-1106-preview",
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    response = gpt_response.choices[0].message.content
    return response


def get_summary(input_text):
    prompt = f"""Find out what kind of document is represented with the input text. The language of the document is most likely German. Generate two German keywords that summarize the document best. Use only single words without special characters as keywords. Create also a short summary in German of the content. 

Use the following example for the json output format:
keywords = [keyword1, keyword2, keyword3]
summary = "A short summary of the input text"

Output as json with the following keys:
keywords, summary                

Input:
{input_text} 
"""
    response = get_response(prompt)
    return response


if __name__ == "__main__":
    logging.basicConfig(
        filename="archive_documents.log",
        format="%(asctime)s%(levelname)s:%(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        encoding="utf-8",
        level=logging.DEBUG,
    )

    logging.debug(f"get_summary_from_text.py called")

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="Input path")
    parser.add_argument(
        "in_file_to_process", help="File containing filename to process"
    )
    args = parser.parse_args()

    with open(args.in_file_to_process, "r") as read_file:
        process_filename = read_file.readline()
    input_name = os.path.join(args.input_dir, process_filename)

    logging.debug(f"get_summary_from_text.py process: {process_filename}")

    with open(input_name, "r") as read_file:
        data = json.load(read_file)

    data = data["responses"]
    data = data[0]
    data = data["fullTextAnnotation"]
    text = data["text"]

    # replace names
    text = text.replace("example1", "abcdef1")
    text = text.replace("example2", "abcdef2")
    text = text.replace("example3", "abcdef3")
    text = text.replace("example4", "abcdef4")

    out_json = get_summary(text)

    if not out_json:
        sys.exit(1)

    # undo replaced names
    out_json = out_json.replace("abcdef1", "example1")
    out_json = out_json.replace("abcdef2", "example2")
    out_json = out_json.replace("abcdef3", "example3")
    out_json = out_json.replace("abcdef4", "example4")

    out_file, _ = os.path.splitext(input_name)
    out_file = out_file + "_summary.json"

    with open(out_file, "w") as json_file:
        json_file.writelines(out_json)

    logging.debug("get_summary_from_text.py successfully finished")
