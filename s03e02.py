import os
import zipfile

import openai
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from qdrant_client.models import VectorParams, Distance

from AIService import AIService
from messenger import verify_task

PROMPT_THEFT = """You are a helpful assistant that provide Yes/No answers.
Rules
1. Answer 'Yes' only if you detect mention about theft in the given Polish text. 
2. Answer No otherwise.
"""
PROMPT_WEAPON = """You are a helpful assistant that retrieves name of the weapon from the input report.
Return only name of the weapon, nothing else.
"""
file_path = 'resources/s03e02'
folder_path = f'{file_path}/do-not-share'
question = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
collection_name = "weapons_test_results"
embedding_model = "text-embedding-3-small"
openai.api_key = os.getenv("openai.api_key")


def retrieve_data(url) -> []:
    zip_file_path = os.path.basename(url)
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Write the zip file to disk
    with open(zip_file_path, "wb") as file:
        file.write(response.content)

    # Extract the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(file_path)

    # Clean up the zip file
    os.remove(zip_file_path)
    return [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.zip')]


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
                text = file_name.split('.txt')[0].replace('_', '-') + ":" + file.read()
                file_contents.append(text.replace('\n', ' '))
    return file_contents


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
                "theft": service.answer(text, PROMPT_THEFT),
                "weapon": service.answer(text, PROMPT_WEAPON)
            },
        )
        for idx, (data, text) in enumerate(zip(result.data, texts))
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
files = retrieve_data(os.environ.get("aidevs.factory_files_url"))
unzip_files_with_password(files, file_path)
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
response_data = verify_task(
    "wektory", answer, os.environ.get("aidevs.report_url"))
print(response_data)
