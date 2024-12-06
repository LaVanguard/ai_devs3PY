import os
import zipfile

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

KEYWORDS_PROMPT = """Extract all the information from the document in Polish, building a map of Polish keywords related to people, 
their fate and their occupation. Input contains paragraphs called facts. Each paragraph (fact) should have as many keywords as possible. Ignore deleted records.
Rules:
- Each keyword must be in nominative case in Polish.
- Categorize keywords per person
- Provide as many keywords as possible.
- Do not include any other information than keywords.
"""
PROMPT = """Match provided information with the categorized keywords. 
Your task is to generate keywords for the given reports. Each report consist of the file name followed by a colon and
the report itself. Retrieve name of the sector from the file name. There must be exactly one list of keywords for each report. 
If you find a match, include keywords from the <categorizedKeywords> too. 
Rules:
- Ignore deleted records
- Include sector name from file name as a keyword.
- Each keyword must be in nominative case in Polish.
- If report consists of a person from categorized keywords, include all those keywords in the output
- Provide as many keywords as possible.
- Provide answer in the following format ignoring new line characters:
{
"nazwa-pliku-01.txt":"lista, słów, kluczowych 1",
"nazwa-pliku-02.txt":"lista, słów, kluczowych 2",
"nazwa-pliku-03.txt":"lista, słów, kluczowych 3",
"nazwa-pliku-NN.txt":"lista, słów, kluczowych N"
}"""
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


def keywords_from_facts() -> str:
    concatenated_text = ""
    for file_name in os.listdir(facts_folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(facts_folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                concatenated_text += file.read()
    print("facts:\n" + concatenated_text)
    return AIService().answer(concatenated_text, KEYWORDS_PROMPT, AIService.AIModel.GPT4o)


def build_reports(files) -> str:
    reports = ''
    for file in files:
        file_name = os.path.basename(file)
        with open(file, 'r', encoding='utf-8') as f:
            reports += file_name + ": " + f.read() + "\n"
    return reports


load_dotenv()

files = retrieve_data(os.environ.get("aidevs.factory_files_url"))
factsKeywords = keywords_from_facts()
print("keywords:\n" + factsKeywords)
context = f"<categorizedKeywords>${factsKeywords}</categorizedKeywords>\n" + PROMPT
reports = build_reports(files)
print("reports:\n" + reports)
keywords = AIService().answer(reports, context, AIService.AIModel.GPT4o)
print(keywords)

response_data = verify_task("dokumenty", json_loads(keywords))
print(response_data)
