import json
import os

from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task, get_file_data

MODEL = AIService.AIModel.DALLE3
working_dir = f"resources/s02e03"


def retrieve_data() -> str:
    content = ""
    file_name = os.environ.get("aidevs.s02e03.file_name")
    file_path = os.path.join(working_dir, file_name)
    os.makedirs(working_dir, exist_ok=True)
    if not os.path.exists(file_path):
        content = get_file_data(file_name, True)

        # Create the file and write the content to it
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json.loads(content), file, ensure_ascii=False, indent=4)
    else:
        # Read the content of the file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
    return json.loads(content).get("description")


load_dotenv()
data = retrieve_data()
print(data)
img_url = AIService().generateImage(data, MODEL)
print(img_url)

response_data = verify_task("robotid", img_url)
print(response_data)
