import os

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

PROMPT = """You are a police censor. Your job is to return the censored content you receive.
         It's very important to return the exact same content, in the same form, and without your comment. 
         Keep the same punctuation and don't decline words.
         Replace any sensitive data with the word 'CENZURA'. Sensitive data includes: 
         - name and surname
         - address and number
         - city
         - number of years age
         Use exact word 'CENZURA' and do not decline it. Avoid repetition of the word CENZURA."""

load_dotenv()


# Fetch the content from the specified URL
def retrieve_data() -> str:
    response = requests.get(os.environ.get("aidevs.s01e05.url"))
    return response.text


data = retrieve_data()
print(data)
message = AIService().answer(data, PROMPT, AIService.AIModel.LLAMA32)
print(message)
response_data = verify_task("CENZURA", message, os.environ.get("aidevs.report_url"))
print(response_data)
