import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()
url = os.environ.get("aidevs.dane_url")
arr = requests.get(url).text.strip().split("\n")

def verify_task(task, answer):
    json_obj = {
      "task": task,
      "apikey": os.environ.get("aidevs.api_key"),
      "answer": answer
    }

    json_json = json.dumps(json_obj)
    response = requests.post(os.environ.get("aidevs.verify_url"),
        data=json_json,
        headers={"Content-Type": "application/json"},
    )
    print(response.json())


verify_task("POLIGON", arr)