import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from AIService import AIService

PROMPT = "You are a helpful assistant. Provide answer to the question in the format yyyy."

load_dotenv()


def retrieve_question() -> str:
    global response, question
    response = requests.get(os.environ.get("aidevs.xyz_url"))
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find("p", {"id": "human-question"}).get_text()


# Get Question from existing form
question = retrieve_question()

# Find answer using llm
answer = AIService().answer(question, PROMPT)  # Find answer using llm

# submit form with data to bypass security reverse captcha
form_data = {
    "username": os.environ.get("aidevs.xyz_login"),
    "password": os.environ.get("aidevs.xyz_password"),
    "answer": answer
}
response = requests.post(os.environ.get("aidevs.xyz_url"), data=form_data)
print(response.text)
