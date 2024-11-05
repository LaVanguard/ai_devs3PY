import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

response = requests.get(os.environ.get("aidevs.xyz_url"))
session = requests.Session()
soup = BeautifulSoup(response.text, 'html.parser')
question = soup.find("p", {"id": "human-question"}).get_text()

openaiclient = OpenAI(api_key=os.environ.get("openai.api_key"))

completion = openaiclient.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": os.environ.get("aidevs.s01e01.prompt") + question,
        }
    ],
    model=os.environ.get("aidevs.s01e01.model")
)

answer = completion.choices[0].message.content.strip()

username = os.environ.get("aidevs.xyz_login")
password = os.environ.get("aidevs.xyz_pass")
form_data = {
    "username": username,
    "answer": answer,
    "password": password
}
response = session.post(os.environ.get("aidevs.xyz_url"),
                        data=form_data
                        )
print(response.text)
