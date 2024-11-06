import os

import requests
from dotenv import load_dotenv

from messenger import verify_task

load_dotenv()

arr = requests.get(os.environ.get("aidevs.dane_url")).text.strip().split("\n")

response_data = verify_task("POLIGON", arr, os.environ.get("aidevs.verify_url"))
print(response_data)
