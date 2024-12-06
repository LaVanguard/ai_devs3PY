import os

import requests
from bs4 import BeautifulSoup
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from AIStrategy import AIStrategy
from MP3ToTextStrategy import MP3ToTextStrategy
from PNGToTextStrategy import PNGToTextStrategy
from messenger import verify_task, get_file_data, get_file_content

ARTICLE_URL = os.environ.get("aidevs.s02e05.article_url")
PROMPT = """You are a helpful data analyst. Analyze the provided article to answer the questions given in the following format
01=What is the first question?
02=What is the second question? 
...
10=What is the tenth question?

The article is divided into sections. Audio and image files are included in the article as text. Based on the article, answer the questions and provide 
the answers in the following format skipping the new line characters:
{
"01": "Answer to the first question",
"02": "Answer to the second question",
"03": "Answer to the third question",
}

Pay special attention to the context of images and audio files.
Context: {context}
"""

working_dir = 'resources/s02e05'


class Context():

    def __init__(self) -> None:
        self._strategyDict = {}

    def register(self, strategy: AIStrategy) -> None:
        self._strategyDict[strategy.medium] = strategy

    def convert(self, file: str) -> str:
        ext = os.path.splitext(file)[1]
        strategy = self._strategyDict.get(ext)
        if strategy is None:
            return ""
        return strategy.convert(file)

    def build(self, article_file_name: str) -> str:
        context = PROMPT
        sections = []
        soup = BeautifulSoup(get_file_data(article_file_name), 'html.parser')
        soup = self.strip_p_tags(soup)
        container = soup.find('div', class_='container')
        if not container:
            return ""

        current_section = {'title': '', 'text': ''}
        for element in container.descendants:
            if element.name == 'h1':
                current_section = self.process_h1(element, current_section, sections)
            elif element.name == 'h2':
                current_section = self.process_h2(element, current_section, sections)
            elif element.name == 'figure':
                current_section = self.process_figure(element, current_section)
            elif element.name == 'audio' and 'controls' in element.attrs:
                current_section = self.process_audio(element, current_section)
            elif element.string:
                current_section['text'] += element.string.strip() + ' '

        if current_section['text']:
            sections.append(current_section)

        for section in sections:
            context += f"Section: {section['title']}\n"
            context += " ".join(section['text']) + "\n"
        return context

    def strip_p_tags(self, soup):
        for p in soup.find_all('p'):
            p.unwrap()  # Remove the <p> tag but keep its content
        return soup

    def process_h1(self, element, current_section, sections):
        current_section['title'] = element.get_text(strip=True)
        return current_section

    def process_h2(self, element, current_section, sections):
        if current_section['text']:
            sections.append(current_section)
        return {'title': element.get_text(strip=True), 'text': ''}

    def process_figure(self, element, current_section):
        img_tag = element.find('img')
        figcaption_tag = element.find('figcaption')
        if img_tag and figcaption_tag:
            file_name = img_tag['src']
            img_file_path = retrieve_and_save_file(file_name)
            current_section[
                'text'] += f"Image (caption: {figcaption_tag.get_text(strip=True)}): {self.convert(img_file_path)} "
        return current_section

    def process_audio(self, element, current_section):
        source_tag = element.find('source')
        if source_tag and 'src' in source_tag.attrs:
            file_name = source_tag['src']
            audio_file_path = retrieve_and_save_file(file_name)
            current_section['text'] += f"Audio transcription: {self.convert(audio_file_path)} "
        return current_section


def retrieve_and_save_file(resource_name) -> str:
    content = get_file_content(resource_name)
    file_name = os.path.basename(resource_name)
    file_path = os.path.join(working_dir, file_name)
    os.makedirs(working_dir, exist_ok=True)
    with open(file_path, "wb") as file:
        file.write(content)
    return file_path


def retrieve_text(article_url) -> []:
    # Fetch the content from the specified URL
    response = requests.get(article_url)
    response.raise_for_status()  # Ensure the request was successful
    return response.text


load_dotenv()
questions = get_file_data(os.environ.get("aidevs.s02e05.questions_file_name"), True)
context = Context()
context.register(MP3ToTextStrategy())
context.register(PNGToTextStrategy())
contextString = context.build(os.environ.get("aidevs.s02e05.article_file_name"))
answers = AIService().answer(questions, contextString)

print(questions)
print(answers)

response_data = verify_task(
    "arxiv", json_loads(answers), os.environ.get("aidevs.report_url"))
print(response_data)
