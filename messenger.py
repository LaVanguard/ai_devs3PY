import json
import os
from typing import Any
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from markdownify import markdownify
from requests import Response

load_dotenv()


def prepare_query(instruction) -> dict[str, str | None | Any]:
    global query_payload
    query_payload = {
        "task": "database",
        "apikey": os.environ.get("aidevs.api_key"),
        "query": instruction
    }
    return query_payload


def db_show_create_table(url, table) -> Response:
    return db_query(url, f"show create table {table}")


def db_query(url, query) -> Response:
    return requests.post(url, json=prepare_query(query))


def construct_data_url(filename, include_api_key):
    if include_api_key:
        base = urljoin(os.environ.get("aidevs.secure_data_url"), f"{os.getenv("aidevs.api_key")}/")
        return urljoin(base, filename)
    else:
        return urljoin(os.environ.get("aidevs.data_url"), filename)


def get_response(filename, include_api_key):
    url = construct_data_url(filename, include_api_key)
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return response


def get_text(url) -> str:
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_markdown(url) -> str:
    return markdownify(get_text(url))


def get_file_data(file_name, include_api_key=False) -> str:
    response = get_response(file_name, include_api_key)
    return response.text


def get_file_content(file_name, include_api_key=False) -> bytes:
    response = get_response(file_name, include_api_key)
    return response.content


def verify(data, url):
    response = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    return response.json()


def verify_task(task, answer, url=os.environ.get("aidevs.report_url")):
    json_obj = {
        "task": task,
        "apikey": os.environ.get("aidevs.api_key"),
        "answer": answer
    }

    data = json.dumps(json_obj)
    response = requests.post(url,
                             data=data,
                             headers={"Content-Type": "application/json"},
                             ).json()
    print(response)
    return response
