import base64
import os
import zipfile
from functools import partial

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

TXT_PROMPT = """You are helpful specialist of human and machine activity recognition.
You categorize reports according to type of activity: human, machine or neither.
"""

PROMPT = """You are data analyst. Analyze the following reports and provide categorized summary of the data.
If activity refers to machines categorize as "hardware".
If activity refers to humans categorize as "people".
IO activity is neither human nor hardware do not include it in the summary.
Present result structuring content as follows:
{
  "people": ["plik1.txt", "plik2.mp3", "plikN.png"],
  "hardware": ["plik4.txt", "plik5.png", "plik6.mp3"],
}
"""
file_path = 'resources/s02e04'
zip_file_path = 'resources/s02e04/s02e04.zip'
context = "Taking into consideration the following reports"
aiservice = AIService()
# Map file extensions to AIService methods with parameters
file_handlers = {
    '.txt': partial(aiservice.answer, prompt=TXT_PROMPT, model=AIService.AIModel.GPT4o),
    '.mp3': partial(aiservice.transcribe),
    '.png': partial(aiservice.describeImage, data_type=AIService.IMG_TYPE_PNG, question=AIService.IMG_QUESTION,
                    prompt=TXT_PROMPT,
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
    handler = file_handlers.get(ext)
    if handler:
        result = ""
        if ext == '.txt':
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                result = handler(content)
                context += os.path.basename(file) + ": " + result + "\n"
        if ext == '.mp3':
            with open(file, 'rb') as f:
                result = handler(f)
                context += os.path.basename(file) + ": " + result + "\n"
        if ext == '.png':
            with open(file, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
                result = handler(content)
                context += os.path.basename(file) + ": " + result + "\n"
        print(f"Result for {file}: {result}")

print(context)

json = aiservice.answer(context, PROMPT)
print("Final report: ")
print(json)
response_data = verify_task(
    "kategorie", context, os.environ.get("aidevs.report_url"))
print(response_data)

# print(data)
# img_url = AIService().generateImage(data, MODEL)
# print(img_url)
#
# response_data = verify_task(
#     "robotid", img_url, os.environ.get("aidevs.report_url"))
# print(response_data)
