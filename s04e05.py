import json
import os

import pytesseract
from deepdiff.serialization import json_loads
from dotenv import load_dotenv
from pdf2image import convert_from_path

from messenger import get_file_text, verify_task, get_file_bytes

load_dotenv()


def get_working_dir() -> str:
    working_dir = "resources/s04e05"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def retrieve_data(file_name):
    working_dir = get_working_dir()
    file_path = os.path.join(get_working_dir(), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        json_text = json_loads(get_file_text(file_name, False))
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_text, file, ensure_ascii=False, indent=2)
        return json_text


def retrieve_pdf(file_url):
    working_dir = get_working_dir()
    file_name = os.path.basename(file_url)
    file_path = os.path.join(working_dir, file_name)

    # Download the PDF file from the URL
    content = get_file_bytes(file_url)
    with open(file_path, 'wb') as file:
        file.write(content)

    return file_path


def extract_text_from_pdf(file_path):
    # Convert PDF to images
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text


pdf_file_path = retrieve_pdf(os.environ.get("aidevs.s04e05.notepad_file_name"))
retrieve_data(os.environ.get("aidevs.s04e05.file_name"))
# response
# pdf_text = extract_text_from_pdf(pdf_file_path)
# print(pdf_text)
# answer = {"01": "2019", "02": "Adam",
#           "03": "Rafał znalazł schronienie w jaskini w lesie oddalonym od miasta, w którym spędził ostatnie lata. Opisał to miejsce jako zimne, ciemne, ale bezpieczne",
#           "04": "2024-11-12",
#           "05": "Lubawa koło Grudziądza"}
answer = {}
verify_task("notes", answer)
