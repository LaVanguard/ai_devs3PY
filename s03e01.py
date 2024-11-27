import os
import zipfile

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

PROMPT = """You are a data analyst helping summarize reports. Each report consist of the file name of the report and
the report itself. Your work is not generate 5 keywords for each report. Each keyword must be in nominative case in Polish.
Provide answer in the following format ignoring new line characters:
{
"nazwa-pliku-01.txt":"wykrycie, alarm, zabezpieczenie, kamera, monitoring",
"nazwa-pliku-02.txt":"obszar, patrolowanie, anomalia, skaner, kontrola",
"nazwa-pliku-03.txt":"obserwacja, czujnik, peryferia, mechaniczny, zabezpieczenie",
"nazwa-pliku-NN.txt":"zdarzenie, reakcja, godzina, sygnał, kontrola"
}

<important>
Pay special attention to any anomalies, arrests or human activities and take into consideration the following facts when analysing the reports:
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
                concatenated_text += file.read() + "\n"
    return concatenated_text


def build_reports(files) -> str:
    reports = ''
    for file in files:
        file_name = os.path.basename(file)
        with open(file, 'r', encoding='utf-8') as f:
            reports += file_name + "\n"
            reports += f.read() + "\n"
    return reports


load_dotenv()

files = retrieve_data(os.environ.get("aidevs.factory_files_url"))
facts = concatenate_texts_from_facts()
context = PROMPT + facts
reports = build_reports(files)
print(facts)
keywords = AIService().answer(reports, context)
print(keywords)

response_data = verify_task("dokumenty", json_loads(keywords), os.environ.get("aidevs.report_url"))
print(response_data)
