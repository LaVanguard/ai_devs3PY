import os
import zipfile
from datetime import datetime

import openai
from deepdiff.serialization import json_loads
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from qdrant_client.models import VectorParams, Distance

from AIService import AIService
from messenger import verify_task, get_file_content

PROMPT = """You are a helpful assistant that analyse Polish text and provide 2 information:
1. 'Yes' only if you detect a mention about a theft in the given report, 'No' otherwise.
2. Name of the weapon from the input report.

Example output:
{"Theft": "Yes", "Weapon": "Oscylator energetyczny"}
{"Theft": "No", "Weapon": "Miotacz plazmy"}
{"Theft": "Yes", "Weapon": "Zakrzywiony miecz"}
"""

working_dir = 'resources/s03e02'
folder_path = f'{working_dir}/do-not-share'
question = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
collection_name = "weapons_test_results"
embedding_model = "text-embedding-3-small"
openai.api_key = os.getenv("openai.api_key")
date_format_underscores = "%Y_%m_%d"
date_format_dashes = "%Y-%m-%d"


def retrieve_data(file_name) -> []:
    zip_file_path = os.path.join(working_dir, file_name)
    content = get_file_content(file_name)
    os.makedirs(working_dir, exist_ok=True)
    # Write the zip file to disk
    with open(zip_file_path, "wb") as file:
        file.write(content)

    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(working_dir)

    # Clean up the zip file
    os.remove(zip_file_path)
    return [os.path.join(working_dir, f) for f in os.listdir(working_dir) if f.endswith('.zip')]


def unzip_files_with_password(zip_files, extract_to_path):
    for zip_file_path in zip_files:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.setpassword(os.environ.get("aidevs.factory_files_zip_password").encode())
            zip_ref.extractall(extract_to_path)


def read_files_from_folder(folder_path):
    file_contents = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = f"{format_date(file_name)}:{replace_new_lines(file.read())}"
                file_contents.append(text)
    return file_contents


def replace_new_lines(text):
    return text.replace('\n', ' ')


def format_date(file_name):
    date_obj = datetime.strptime(file_name.split('.txt')[0], date_format_underscores)
    formatted_date = date_obj.strftime(date_format_dashes)
    return formatted_date


# Function to create embeddings using OpenAI
def create_embeddings(texts):
    return openai.embeddings.create(
        input=texts,
        model=embedding_model
    )


service = AIService()


def create_points(result, texts):
    return [
        PointStruct(
            id=idx,
            vector=data.embedding,
            payload={
                "text": text,
                "date": text.split(':')[0],
                "theft": answer.get("Theft"),
                "weapon": answer.get("Weapon")
            },
        )
        for idx, (data, text) in enumerate(zip(result.data, texts))
        if (answer := json_loads(service.answer(text, PROMPT)))
    ]


def create_collection(collection_name):
    collections = qdrant.get_collections().collections
    collection_names = [collection.name for collection in collections]
    if collection_name in collection_names:
        qdrant.delete_collection(collection_name)
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.DOT),
    )


def insert_points(collection_name):
    qdrant.upsert(
        collection_name=collection_name,
        points=points
    )


def answer_question(question, collection_name) -> str:
    answers = qdrant.search(
        collection_name=collection_name,
        query_vector=create_embeddings([question]).data[0].embedding,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="theft",
                    match=models.MatchValue(
                        value="Yes",
                    ),
                )
            ]
        ),
        limit=1,
    )
    return answers[0].payload.get('date')


load_dotenv()
files = retrieve_data(os.environ.get("aidevs.factory_files_file_name"))
unzip_files_with_password(files, working_dir)
texts = read_files_from_folder(folder_path)
result = create_embeddings(texts)
points = create_points(result, texts)

qdrant = QdrantClient(
    url=os.getenv("aidevs.qdrant.db.url"),
    api_key=os.getenv("aidevs.qdrant.api.key")
)
create_collection(collection_name)
insert_points(collection_name)
answer = answer_question(question, collection_name)
response_data = verify_task("wektory", answer)
print(response_data)
