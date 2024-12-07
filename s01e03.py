import json
import os

from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task
from utils import get_or_create_file

PROMPT = "You are helpful assistant. Provide answer to the given questions."

load_dotenv()


def get_working_dir() -> str:
    working_dir = f"resources/s01e03"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def retrieve_data() -> str:
    api_key = os.environ.get("aidevs.api_key")
    api_key_pattern = os.environ.get("aidevs.api_key_pattern")
    file_name = os.environ.get("aidevs.s01e03.file_name")
    content = get_or_create_file(get_working_dir(), file_name)
    return json.loads(content.replace(api_key_pattern, api_key))


def fix_data(data):
    aiservice = AIService()
    for item in data["test-data"]:
        recalculate_math_operation(item)
        answer_additional_question(aiservice, item)


def recalculate_math_operation(item):
    # Calculate the result of the question
    item["answer"] = str(eval(item["question"]))


def answer_additional_question(aiservice, item):
    # For those lines that have additional questions, get answers from llm
    if "test" in item:
        item["test"]["a"] = aiservice.answer(item["test"]["q"])


data = retrieve_data()
fix_data(data)
response_data = verify_task("JSON", data)
print(response_data)
