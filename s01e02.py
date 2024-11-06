import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# response = requests.get(os.environ.get("aidevs.s01e02.soft_url"))
prompt = os.environ.get("aidevs.s01e02.prompt")

openaiclient = OpenAI(api_key=os.environ.get("openai.api_key"))
completion = openaiclient.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": prompt,
        }
    ],
    model=os.environ.get("aidevs.s01e02.model")
)

auth_message = {
    "msgID": 0,
    "text": "READY"
}
verify_url = os.environ.get("aidevs.xyz_verify_url")

response = requests.post(verify_url,
                         data=json.dumps(auth_message), headers={"Content-Type": "application/json"}
                         )
response_data = response.json()
auth_message = {
    "msgID": response_data.get("msgID"),
    "text": completion.choices[0].message.content.strip()
}
response = requests.post(verify_url, data=json.dumps(auth_message), headers={"Content-Type": "application/json"})
response_data = response.json()

print(response_data)
