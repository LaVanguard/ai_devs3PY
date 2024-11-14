import json
import os

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

MODEL = AIService.AIModel.DALLE3
file_path = f"resources/s02e03/s02e03.json"


def retrieve_data() -> str:
    content = ""

    if not os.path.exists(file_path):
        # Fetch the content from the specified URL
        url = os.environ.get("aidevs.s02e03.url")
        response = requests.get(url)
        content = response.text

        # Create the file and write the content to it
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json.loads(content), file, ensure_ascii=False, indent=4)
    else:
        # Read the content of the file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    return json.loads(content).get("description")


load_dotenv()
data = retrieve_data()
print(data)
img_url = AIService().generateImage(data, MODEL)
print(img_url)

response_data = verify_task(
    "robotid", img_url, os.environ.get("aidevs.report_url"))
print(response_data)
