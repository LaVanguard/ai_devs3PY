import os
import zipfile
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI

from messenger import get_file_content
from messenger import verify_task

PRMOPT = """


"""
load_dotenv()

client = OpenAI(api_key=os.environ.get("openai.api_key"))


def get_working_dir() -> str:
    working_dir = "resources/s04e04"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


# Download the ZIP file
def retrieve_data():
    working_dir = get_working_dir()
    if len(os.listdir(working_dir)) == 0:
        content = get_file_content(os.environ.get("aidevs.s04e02.file_name"))
        zip_file = BytesIO(content)
        # Step 2: Unpack the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(working_dir)


answer = ""
verify_task("webhook", answer)
