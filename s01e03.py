import json
import os

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

PROMPT = "You are helpful assistant. Provide answer to the given questions."

load_dotenv()
api_key = os.environ.get("aidevs.api_key")
api_key_pattern = os.environ.get("aidevs.s01e03.api_key_pattern")


def read_file() -> str:
    content = ""
    file_path = f"s01e03.txt"
    if not os.path.exists(file_path):
        # Fetch the content from the specified URL
        url = os.environ.get("aidevs.s01e03.file_url_prefix").replace(api_key_pattern, api_key)
        response = requests.get(url)
        content = response.text

        # Create the file and write the content to it
        with open(file_path, "w") as file:
            file.write(content)
    else:
        # Read the content of the file
        with open(file_path, "r") as file:
            content = file.read()
    return content


text = read_file().replace(api_key_pattern, api_key)
data = json.loads(text)

aiservice = AIService()

for item in data["test-data"]:
    # Calculate the result of the question
    item["answer"] = str(eval(item["question"]))
    # For those lines that have additional questions, get answers from llm
    if "test" in item:
        item["test"]["a"] = aiservice.answer(item["test"]["q"])

response_data = verify_task("JSON", data, os.environ.get("aidevs.s01e03.report_url"))
print(response_data)
