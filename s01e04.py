import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

PROMPT = "You are helpful assistant. Provide answer to the given questions."

load_dotenv()

response = requests.get(os.environ.get("aidevs.s01e04.url"))
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find("div", {"id": "map"}).encode_contents()
print(table)
# response_data = verify_task("JSON", data, os.environ.get("aidevs.s01e03.report_url"))
# print(response_data)
