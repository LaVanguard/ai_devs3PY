import os
import zipfile

import requests
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from AIStrategy import AIStrategy
from MP3ToTextStrategy import MP3ToTextStrategy
from PNGToTextStrategy import PNGToTextStrategy
from TXTToTextStrategy import TXTToTextStrategy
from messenger import verify_task

PROMPT = """You are a helpful data analyst. Analyze reports to provide categorized summary of the data.
Each report section consists of a source file name followed by a colon and the content of the report.
Pay special attention to the reports containing information about captured people or traces of their presence and 
repaired hardware faults since this is the information that should be included in the summary.
Follow strictly the rules:
1. If the activity is related to hardware fault categorize it as "hardware".
2. If the activity is related to software ignore it.
3. If the activity ends up with seizing people or finding traces of people's presence categorize it as "people".
4. If the activity is related to people but does not involve seizing or finding traces of people's presence ignore it.
5. Do not include in the summary any other activities.

Present the results structuring the content as follows:
{"people": ["file1.txt", "file2.mp3", "file3.png"],"hardware": ["file4.txt", "file5.png", "file6.mp3"]}
"""
file_path = 'resources/s02e04'


class Context():

    def __init__(self) -> None:
        self._strategyDict = {}

    def register(self, strategy: AIStrategy) -> None:
        self._strategyDict[strategy.medium] = strategy

    def build(self, files: str) -> str:
        context = ""
        for file in files:
            ext = os.path.splitext(file)[1]
            strategy = self._strategyDict.get(ext)
            if strategy is None:
                continue
            result = os.path.basename(file) + ": " + strategy.convert(file) + "\n"
            print(f"Result for {file}: {result}")
            context += result
        return context


def retrieve_data(url) -> []:
    # Fetch the content from the specified URL
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
    return [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]


context = Context()
context.register(MP3ToTextStrategy())
context.register(PNGToTextStrategy())
context.register(TXTToTextStrategy())

load_dotenv()
files = retrieve_data(os.environ.get("aidevs.factory_files_url"))
question = context.build(files)

answer = AIService().answer(question, PROMPT)
print("Final report: ")
print(answer)

response_data = verify_task("kategorie", json_loads(answer))
print(response_data)
