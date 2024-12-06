import os
from typing import Any

import requests
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

question = "które aktywne datacenter (DC_ID) są zarządzane przez pracowników, którzy są na urlopie (is_active=0)"

PROMPT = f"""You are a SQL expert providing correct SQL syntax. 
Analyse provided database schema to create an an SQL query that answers the question in Polish: <question>{question}</question>. 
Rules:
1. Return only SQL syntax
2. Do not include any other information
3. Do not include new line characters


Format result as per example:
SELECT * FROM users WHERE is_active = '0'
SELECT * FROM table_name WHERE column_name = 'value'
"""
load_dotenv()

api_url = os.getenv("aidevs.apidb.url")
api_key = os.getenv("aidevs.api_key")


def prepare_query(instruction) -> dict[str, str | None | Any]:
    global query_payload
    query_payload = {
        "task": "database",
        "apikey": api_key,
        "query": instruction
    }
    return query_payload


response = requests.post(api_url, json=prepare_query("show tables"))
response_data = response.json()['reply']
table_key = list(response_data[0].keys())[0]
tables = [item[table_key] for item in response_data]

schema = ""
for table in tables:
    response = requests.post(api_url, json=prepare_query(f"show create table {table}"))
    schema += response.json()['reply'][0]['Create Table'] + "\n"

service = AIService()
answertxt = service.answer(schema, PROMPT)
print(answertxt)
response = requests.post(api_url, json=prepare_query(answertxt))
data = response.json()['reply']
answer = [item['dc_id'] for item in data]

response_data = verify_task("database", answer)
print(response_data)
