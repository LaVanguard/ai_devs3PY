import base64
import json
import os
from json import JSONDecodeError

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

IMG_TOOL_PROMPT = """You are a helpful assistant. 
Analyse given answer and find urls of all the images that can be downloaded.
If you found the image name but the URL domain information is missing, find the domain in the past answer history.
Return JSON object and nothing else.
Expected outputs:
{"images": ["https://example.com/image1.png", "https://example.com/image2.jpg"]}
{"images": []}
"""

IMG_CATEGORIZATION_PROMPT = """You are a photo editor assessing quality of images. 
Analyse image available through the given link in terms of quality and suggest improvements.
You've got four modes that you can use:
BRIGHTEN - if the image is too dark
DARKEN - if the image is too bright
REPAIR - if the image is damaged
NONE - if the image is fine

In addition, confirm whether the picture contains a face close-up that could be used to describe a person's face mimic.   
Do not recognize the person, just confirm if the image contains a face close-up.
For this purpose set containsFace flag to True if the image contains a face and False otherwise.

Return JSON object and nothing else.
Expected outputs:
{"action": "BRIGHTEN", "containsFace": "True"}
{"action": "DARKEN", "containsFace": "False"}
{"action": "REPAIR", "containsFace": "False"}
{"action": "NONE", "containsFace": "True"}
"""

PERSON_RECOGNICTION_PROMPT = """You are a painting expert. 
Your task is to describe a person's look based on the given image of a painting. 
Ignore the background and focus only on the person's face. 
Pay special attention to unique features of the person's face, such as the colour of the hair, the colour of the eyes or skin, etc.
Present description in Polish language.
"""
PERSON_RECOGNITION_SUMMARY_PROMPT = """You are a helpful assistant. 
Your task is to summarize given person's descriptions removing duplicate information.
Focus only on the information relevant to person's appearance that seems to describe the same person. 
Present result in Polish language.
"""
load_dotenv()


def get_working_dir() -> str:
    working_dir = "resources/s04e01"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def download_image(url, save_dir=get_working_dir()) -> str:
    response = requests.get(url)
    file_path = ""
    if response.status_code == 200:
        file_path = os.path.join(save_dir, url.split("/")[-1])
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_path}")
    else:
        print(f"Failed to download {url}")
    return file_path


def delete_historical_answers(file_name='historical_answers.json'):
    try:
        file_path = os.path.join(get_working_dir(), file_name)
        os.remove(file_path)
    except FileNotFoundError:
        pass


def store_historical_answer(answer, file_name='historical_answers.json'):
    file_path = os.path.join(get_working_dir(), file_name)
    historical_answers = retrieve_historical_answers(file_path)
    historical_answers.append(answer)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(historical_answers, file, ensure_ascii=False, indent=2)


def retrieve_historical_answers(file_path):
    try:
        with open(file_path, 'r') as file:
            historical_answers = json.load(file)
    except FileNotFoundError:
        historical_answers = []
    except JSONDecodeError:
        historical_answers = []

    return historical_answers


def include_historical_answers(prompt, file_name='historical_answers.json'):
    file_path = os.path.join(get_working_dir(), file_name)

    historical_answers = retrieve_historical_answers(file_path)
    # Incorporate historical answers into the prompt or use them to validate new answers
    # For example, you can append historical answers to the prompt
    prompt_with_history = prompt + "\n<answers_history>\n" + "\n".join(
        json.dumps(answer) for answer in historical_answers) + "</answers_history>"
    return prompt_with_history


def communicate_with_tool(command) -> str:
    response_data = verify_task("photos", command)
    print(response_data)
    message = response_data.get("message")
    store_historical_answer(message)
    return message


def retrieve_images(message, prompt=IMG_TOOL_PROMPT):
    response_data = json_loads(service.answer(message, prompt))
    print(response_data)
    return response_data.get("images")


def describe_image(image_path, prompt) -> str:
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        response_data = service.describeImage(image_base64, prompt=prompt)
        print(response_data)
        return response_data


delete_historical_answers()
service = AIService()

message = communicate_with_tool("START")
images = set(retrieve_images(message))
visited_images = set()
useful_images = set()

while images:
    initial_image_count = len(images)
    images_copy = images.copy()
    for image in images_copy:
        if image not in visited_images:
            visited_images.add(image)
            image_path = download_image(image)
            response_data = json_loads(describe_image(image_path, IMG_CATEGORIZATION_PROMPT))
            action = response_data.get("action")
            if action == "NONE" and response_data.get("containsFace") == "True":
                useful_images.add(image)
            message = communicate_with_tool(action + " " + os.path.basename(image))
            prompt = include_historical_answers(IMG_TOOL_PROMPT)
            images.update(retrieve_images(message, prompt))

    if len(images) == initial_image_count:
        break

print(useful_images)
descriptions = ""

for image in useful_images:
    image_path = os.path.join(get_working_dir(), os.path.basename(image))
    response_data = describe_image(image_path, PERSON_RECOGNICTION_PROMPT)
    descriptions += response_data + "\n\n"

response_data = service.answer(descriptions, prompt=PERSON_RECOGNITION_SUMMARY_PROMPT)
print(response_data)
response_data = verify_task("photos", response_data)
print(response_data)
