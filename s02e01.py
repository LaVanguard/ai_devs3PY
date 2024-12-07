import os
import zipfile
from io import BytesIO

from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task, get_file_content

PROMPT = "You are a private investigator. Try to provide answer based on the following witness testify transcriptions. You need to think out loud first to figure out who is right and who is wrong:  \n\n"
QUESTION = "Na jakiej ulicy znajduje się uczelnia, na której wykłada Andrzej Maj?"
SUPPORTED_AUDIO_FORMATS = (".mp3", ".wav", ".m4a")

working_dir = "s02e01"

load_dotenv()

service = AIService()


# Download the ZIP file
def retrieve_recordings():
    if not os.path.exists(working_dir):
        content = get_file_content("aidevs.s02e01.file_name")
        zip_file = BytesIO(content)
        # Step 2: Unpack the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(working_dir)


# Generate transcriptions from sound files
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        response = service.transcribe(audio_file)
    return response


def is_supported_audio_file(file_name):
    return file_name.lower().endswith(SUPPORTED_AUDIO_FORMATS)


# Build a common prompt context for all transcriptions
def transcribe_files() -> []:
    texts = []
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            if is_supported_audio_file(file):
                file_path = os.path.join(root, file)
                transcription = transcribe_audio(file_path)
                texts.append(transcription)
    return texts


retrieve_recordings()
transcriptions = transcribe_files()
common_prompt_context = PROMPT + "\n".join(transcriptions)
print(common_prompt_context)

# Find answer using llm
answer = AIService().answer(QUESTION, common_prompt_context)
print(answer)
response_data = verify_task("mp3", answer)
print(response_data)
