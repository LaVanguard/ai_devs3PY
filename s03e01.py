import os
import zipfile

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

PROMPT = """Please extract all the information from the document relating to people their fate and their occupation. Ignore deleted records. 
Your task is to generate keywords for each report. Each report consist of the file name followed by a colon and
the report itself. Your work is not generate keywords for each report. Each keyword must be in nominative case in Polish. There must be exactly one list of keywords for each report.
<important> Pay special attention to activities that are reported. Instead of names report individual's occupation or the role.
Provide answer in the following format ignoring new line characters:
{
"nazwa-pliku-01.txt":"lista, słów, kluczowych 1",
"nazwa-pliku-02.txt":"lista, słów, kluczowych 2",
"nazwa-pliku-03.txt":"lista, słów, kluczowych 3",
"nazwa-pliku-NN.txt":"lista, słów, kluczowych N"
}
<reports>
"""
file_path = 'resources/s03e01'
facts_folder_path = f'{file_path}/facts'


def retrieve_data(url) -> []:
    zip_file_path = f"{file_path}/{os.path.basename(url)}"
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Write the zip file to disk
    with open(zip_file_path, "wb") as file:
        file.write(response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(file_path)

    # Clean up the zip file
    os.remove(zip_file_path)
    return [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.txt') and 'sektor' in f]


def concatenate_texts_from_facts() -> str:
    concatenated_text = ""
    for file_name in os.listdir(facts_folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(facts_folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                concatenated_text += file.read()
    return concatenated_text


def build_reports(files) -> str:
    reports = ''
    for file in files:
        file_name = os.path.basename(file)
        with open(file, 'r', encoding='utf-8') as f:
            reports += file_name + ": " + f.read() + "\n"
    return reports


load_dotenv()

files = retrieve_data(os.environ.get("aidevs.factory_files_url"))
facts = concatenate_texts_from_facts()
print("facts:\n" + facts)
context = f"<document>${facts}</document>\n" + PROMPT
reports = build_reports(files)
print("reports:\n" + reports)
keywords = AIService().answer(reports, context)
print(keywords)

response_data = verify_task("dokumenty", json_loads(keywords), os.environ.get("aidevs.report_url"))
print(response_data)
