import json
import os
import zipfile
from io import BytesIO

from dotenv import load_dotenv
from openai import OpenAI

from messenger import get_file_bytes
from messenger import verify_task

PRMOPT = """

Sample output:

[
  'identyfikator-01',
  'identyfikator-02',
  'identyfikator-03',
  'identyfikator-0N',
]
"""
load_dotenv()

client = OpenAI(api_key=os.environ.get("openai.api_key"))


def get_working_dir() -> str:
    working_dir = "resources/s04e02"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


#
# def upload_fine_tuning_file() -> str:
#     response = client.files.create(
#         file=open(os.path.join(get_working_dir(), "fine_tuning_data.jsonl"), "rb"),
#         purpose='fine-tune'
#     )
#     file_id = response.id
#     print(f"Uploaded file ID: {file_id}")
#     return file_id
#
#
# def create_fine_tuning_job(file_id) -> str:
#     fine_tune_response = client.fine_tunes.create(
#         training_file=file_id
#     )
#     fine_tune_job_id = fine_tune_response['id']
#     print(f"Fine-tune job ID: {fine_tune_job_id}")
#     return fine_tune_job_id
#
#
# def get_status(fine_tune_job_id):
#     status = client.fine_tune.retrieve(id=fine_tune_job_id)
#     print(f"Status: {status['status']}")
#     return status
#

# Download the ZIP file
def retrieve_data():
    working_dir = get_working_dir()
    if len(os.listdir(working_dir)) == 0:
        content = get_file_bytes(os.environ.get("aidevs.s04e02.file_name"))
        zip_file = BytesIO(content)
        # Step 2: Unpack the ZIP file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(working_dir)


def classify_verification_file(rows, model_id) -> str:
    # status = get_status(fine_tune_job_id)
    # fine_tuned_model = status['fine_tuned_model']
    prompts = [f"Classify the following data: {row.split('=')[1]}" for row in rows]

    # Send batch request (one request for each prompt)
    responses = [
        client.chat.completions.create(
            model=model_id,  # Replace with your fine-tuned model ID
            prompt=prompt,
            max_tokens=1
        )
        for prompt in prompts
    ]

    # Process responses
    results = [response["choices"][0]["text"].strip() for response in responses]

    # Display results
    for row, result in zip(rows, results):
        print(f"Row: {row} --> Classification: {result}")

    return ""


def create_fine_tuning_data(correct_file_path, incorrect_file_path, output_path):
    fine_tuning_data = []

    # Process correct data
    with open(correct_file_path, 'r') as correct_file:
        for line in correct_file:
            data = line.strip()
            fine_tuning_data.append({
                "prompt": f"Classify the following data: {data}",
                "completion": " correct"
            })

    # Process incorrect data
    with open(incorrect_file_path, 'r') as incorrect_file:
        for line in incorrect_file:
            data = line.strip()
            fine_tuning_data.append({
                "prompt": f"Classify the following data: {data}",
                "completion": " incorrect"
            })

    # Save to JSONL file
    with open(output_path, 'w') as output_file:
        for entry in fine_tuning_data:
            output_file.write(json.dumps(entry) + '\n')

    print(f"Fine-tuning data saved to {output_path}")


def create_chat_fine_tuning_data(correct_file_path, incorrect_file_path, output_path):
    chat_data = []

    # Process correct data
    with open(correct_file_path, 'r') as correct_file:
        for line in correct_file:
            data = line.strip()
            chat_data.append({
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Classify the following data: {data}"},
                    {"role": "assistant", "content": "correct"}
                ]
            })

    # Process incorrect data
    with open(incorrect_file_path, 'r') as incorrect_file:
        for line in incorrect_file:
            data = line.strip()
            chat_data.append({
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Classify the following data: {data}"},
                    {"role": "assistant", "content": "incorrect"}
                ]
            })

    # Save to JSONL file
    with open(output_path, 'w') as output_file:
        for entry in chat_data:
            output_file.write(json.dumps(entry) + '\n')

    print(f"Chat-formatted data saved to {output_path}")


retrieve_data()
correct_file = os.path.join(get_working_dir(), "correct.txt")
incorrect_file = os.path.join(get_working_dir(), "incorrect.txt")
verify_file = os.path.join(get_working_dir(), "verify.txt")
fine_tuning_output = os.path.join(get_working_dir(), "fine_tuning_data.jsonl")
chat_output = os.path.join(get_working_dir(), "chat_fine_tuning_data.jsonl")

create_fine_tuning_data(correct_file, incorrect_file, fine_tuning_output)
create_chat_fine_tuning_data(correct_file, incorrect_file, chat_output)
# job_id = "ftjob-w1FPEzWjEsInUEenVAPx7HId"
model_name = os.environ.get("aidevs.s04e02.model_name")
with open(verify_file, 'r') as file:
    lines = file.readlines()
    # classify_verification_file(lines, model_name)
#
# file_id = upload_fine_tuning_file()
# fine_tune_job_id = create_fine_tuning_job(file_id)
# Classify the following data: 12,100,3,39
# Classify the following data: -41,75,67,-25
# Classify the following data: 78,38,65,2
# Classify the following data: 5,64,67,30
# Classify the following data: 33,-21,16,-72
# Classify the following data: 99,17,69,61
# Classify the following data: 17,-42,-65,-43
# Classify the following data: 57,-83,-54,-43
# Classify the following data: 67,-55,-6,-32
# Classify the following data: -20,-23,-2,44

answer = ['01', '02', '10']
verify_task("research", answer)
