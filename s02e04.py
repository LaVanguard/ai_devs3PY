import base64
import os
import zipfile
from functools import partial

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

IMG_PROMPT = """You are helpful text recognition specialist that provides a summary of the recognized content.
"""
PROMPT = """You are a helpful data analyst. Analyze reports to provide categorized summary of the data.
Each report section consists of a source file name followed by a colon and the content of the report.
Pay special attention to the reports containing information about captured people or traces of their presence and 
repaired hardware faults since this is the information that should be included in the summary.
Follow strictly the rules:
1. If the activity is related to hardware fault categorize it as "hardware".
2. If the activity is related to software ignore it.
3. If the activity ends up with seizing people or finding traces of people's presence categorize it as "people".
4. If the activity is related to people but does not involve seizing or finding traces of people's presence ignore it.
5. Do not include in the summary any other activities.

Present the results structuring the content as follows:
{"people": ["file1.txt", "file2.mp3", "file3.png"],"hardware": ["file4.txt", "file5.png", "file6.mp3"]}
"""
file_path = 'resources/s02e04'
zip_file_path = 'resources/s02e04/s02e04.zip'
context = "Taking into consideration the following reports"
aiservice = AIService()
# Map file extensions to AIService methods with parameters
file_handlers = {
    '.txt': partial(aiservice.answer, model=AIService.AIModel.GPT4o),
    '.mp3': partial(aiservice.transcribe),
    '.png': partial(aiservice.describeImage, data_type=AIService.IMG_TYPE_PNG, question=AIService.IMG_QUESTION,
                    prompt=IMG_PROMPT,
                    model=AIService.AIModel.GPT4o)
}


def retrieve_data() -> []:
    # Fetch the content from the specified URL
    url = os.environ.get("aidevs.s02e04.url")
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
    return [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]


load_dotenv()
files = retrieve_data()
for file in files:
    ext = os.path.splitext(file)[1]
    result = ""
    if ext == '.txt':
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # result = handler(content)
            context += os.path.basename(file) + ": " + content + "\n"
    if ext == '.mp3':
        handler = file_handlers.get(ext)
        with open(file, 'rb') as f:
            result = handler(f)
            context += os.path.basename(file) + ": " + result + "\n"
    if ext == '.png':
        handler = file_handlers.get(ext)
        with open(file, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            result = handler(content)
            context += os.path.basename(file) + ": " + result + "\n"
        print(f"Result for {file}: {result}")

print(context)

answer = aiservice.answer(context, PROMPT)
print("Final report: ")
print(answer)
data = json_loads(answer)
print(data)

response_data = verify_task(
    "kategorie", data, os.environ.get("aidevs.report_url"))
print(response_data)
