import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
arr = requests.get(os.environ.get("aidevs.dane_url")).text.strip().split("\n")


def verify(data, url):
    response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    return response.json()


def verify_task(task, answer, url):
    json_obj = {
        "task": task,
        "apikey": os.environ.get("aidevs.api_key"),
        "answer": answer
    }

    json_json = json.dumps(json_obj)
    response = requests.post(url,
                             data=json_json,
                             headers={"Content-Type": "application/json"},
                             )
    return response.json()
