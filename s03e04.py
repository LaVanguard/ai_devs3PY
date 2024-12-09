import os

import requests
from deepdiff.serialization import json_loads, json_dumps
from dotenv import load_dotenv
from unidecode import unidecode

from AIService import AIService
from messenger import verify_task
from utils import get_or_create_file

PROMPT_NOTE = """Your are a helpful assistant. Retrieve city names and people first names in nominative case from the given input text.
All diacritical characters should be changed to their ISO basic Latin alphabet equivalent.

Sample output:
{"people": ["JOHN", "JANE"], "places": ["NEW YORK", "LOS ANGELES"]}
"""

PROMPT = """You are a specialist of finding people. 
Your task is to analyse data containing people chow visited cities and provide answer in which city Barbara might be now.
Try to correlate gathered data, consider even smallest clues and think out loud prior to providing the answer. 
As an output provide the name of the city and nothing else.

Input file structure:
CITY NAME: LIST OF PEOPLE WHO VISITED THE CITY OR RESTRICTED DATA
PERSON NAME: LIST OF CITIES VISITED BY THE PERSON OR RESTRICTED DATA

Expected output:
CITY NAME
"""

load_dotenv()
file_name = "resultaty.txt"
api = {"people": os.getenv("aidevs.people.url"), "places": os.getenv("aidevs.places.url")}
api_key = os.getenv("aidevs.api_key")


def save_to_file(file_name, content):
    file_path = os.path.join(get_working_dir(), file_name)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content)


def get_working_dir() -> str:
    working_dir = "resources/s03e04"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def not_restricted(data) -> bool:
    return "RESTRICTED" not in data


def query_api(query_type, search_term) -> set:
    if query_type not in ["people", "places"]:
        raise ValueError("Invalid query type. Must be 'people' or 'places'.")

    url = api.get(query_type)
    payload = {
        "apikey": api_key,
        "query": search_term
    }
    response_json = requests.post(url, json_dumps(payload)).json()
    data = response_json.get("message")
    print(f"Searching for: {search_term}, got response: {data}")
    save_to_file(file_name, f"{search_term}: {data}\n")
    if not_restricted(data):
        return set(unidecode(data).split(" "))

    return set()


def delete_results_file():
    results_file = os.path.join(get_working_dir(), file_name)
    # Delete the file if it exists
    if os.path.exists(results_file):
        os.remove(results_file)


def iterate_collection(type, collection1, collection2, visited):
    while collection1:
        elem = collection1.pop()
        if elem not in visited:
            new_elems = query_api(type, elem)
            collection2.update(new_elems)
            visited.add(elem)


def generate_location_report(data):
    visited = set()
    people = set(parsed_data.get("people"))
    places = set(parsed_data.get("places"))
    while people or places:
        initial_people_count = len(people)
        initial_places_count = len(places)

        iterate_collection("people", people, places, visited)
        iterate_collection("places", places, people, visited)

        if len(people) == initial_people_count and len(places) == initial_places_count:
            break


def retrive_data_from_note():
    global parsed_data
    text = get_or_create_file(get_working_dir(), os.environ.get("aidevs.s03e04.file_name"))
    parsed_data = json_loads(AIService().answer(text, PROMPT_NOTE))
    print(parsed_data)
    return parsed_data


delete_results_file()
parsed_data = retrive_data_from_note()
generate_location_report(parsed_data)
city_name = AIService().answer(get_or_create_file(get_working_dir(), file_name), PROMPT)
print(city_name)
verify_task("loop", city_name)
