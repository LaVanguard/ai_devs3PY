import os
import zipfile
from io import BytesIO

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

FOLDER = "s02e01_files"

PROMPT = "You are a private investigator. Try to provide answer based on the following witness testify transcriptions:\n\n"
SUPPORTED_AUDIO_FORMATS = (".mp3", ".wav", ".m4a")
load_dotenv()

service = AIService()


# Step 1: Download the ZIP file
def retrieve_recordings():
    if not os.path.exists(FOLDER):
        resp = requests.get(os.environ.get("aidevs.s02e01.url"))
        zip_file = BytesIO(resp.content)
        # Step 2: Unpack the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(FOLDER)


# Step 3: Generate transcriptions from sound files
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        response = service.transcribe(audio_file)
    return response


def is_supported_audio_file(file_name):
    return file_name.lower().endswith(SUPPORTED_AUDIO_FORMATS)


# Step 4: Build a common prompt context for all transcriptions


def transcribe_files() -> []:
    texts = []
    for root, dirs, files in os.walk(FOLDER):
        for file in files:
            if is_supported_audio_file(file):
                file_path = os.path.join(root, file)
                transcription = transcribe_audio(file_path)
                texts.append(transcription)
    return texts


retrieve_recordings()
transcriptions = transcribe_files()
common_prompt_context = PROMPT.join("\n".join(transcriptions))
print(common_prompt_context)
question = "na jakiej ulicy znajduje się uczelnia, na której wykłada Andrzej Maj"
# Find answer using llm
answer = AIService().answer(question, common_prompt_context)

response_data = verify_task(
    "mp3", answer, os.environ.get("aidevs.report_url"))
print(response_data)
