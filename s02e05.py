import base64
import os
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from deepdiff.serialization import json_loads
from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task

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

file_path = 'resources/s02e05'


class AIStrategy(ABC):
    _aiservice = AIService()

    def __init__(self, medium: str) -> None:
        self.medium = medium

    @abstractmethod
    def convert(self, file: str):
        pass

    def medium(self) -> str:
        return self.medium


class MP3ToTextStrategy(AIStrategy):

    def __init__(self):
        super().__init__('.mp3')

    def convert(self, file: str) -> str:
        with open(file, 'rb') as f:
            return self._aiservice.transcribe(f)


class PNGToTextStrategy(AIStrategy):
    def __init__(self):
        super().__init__('.png')

    def convert(self, file: str) -> str:
        with open(file, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            return self._aiservice.describeImage(content, data_type=AIService.IMG_TYPE_PNG,
                                                 question=AIService.IMG_QUESTION,
                                                 prompt=IMG_PROMPT,
                                                 model=AIService.AIModel.GPT4o)


class TXTToTextStrategy(AIStrategy):
    def __init__(self):
        super().__init__('.txt')

    def convert(self, file: str) -> str:
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()


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


def retrieve_questions() -> []:
    # Fetch the content from the specified URL
    url = os.environ.get("aidevs.s02e05.questions_url")
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return response.text


def retrieve_article() -> []:
    # Fetch the content from the specified URL
    url = os.environ.get("aidevs.s02e05.article_url")
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    return response.text


# Function to extract text, images, and audio links
def extract_content(soup):
    text_content = soup.get_text()
    images = [img['src'] for img in soup.find_all('img')]
    audio_links = [audio['src'] for audio in soup.find_all('audio')]
    return text_content, images, audio_links


# Function to process images and audio
def process_media(images, audio_links):
    processed_images = []
    processed_audio = []
    for img in images:
        response = requests.get(img)
        response.raise_for_status()
        content = base64.b64encode(response.content).decode('utf-8')
        processed_images.append(
            AIService().describeImage(content, data_type=AIService.IMG_TYPE_PNG, question=AIService.IMG_QUESTION,
                                      prompt=IMG_PROMPT, model=AIService.AIModel.GPT4o))

    for audio in audio_links:
        response = requests.get(audio)
        response.raise_for_status()
        processed_audio.append(AIService().transcribe(response.content))

    return processed_images, processed_audio


# questions = retrieve_data()
# text_content, images, audio_links = extract_content(soup)
#
# processed_images, processed_audio = process_media(images, audio_links)
#
# # Combine all content into a single context
# context = f"Text: {text_content}\nImages: {processed_images}\nAudio: {processed_audio}"
#
# # Use AIService to answer questions based on the context
# answer = AIService().answer(context, PROMPT)
# print("Final report: ")
# print(answer)
#
# # Verify the task
# response_data = verify_task("arxiv", json_loads(answer), os.environ.get("aidevs.report_url"))
# print(response_data)
context = Context()
context.register(MP3ToTextStrategy())
context.register(PNGToTextStrategy())
context.register(TXTToTextStrategy())


def strip_p_tags(soup):
    for p in soup.find_all('p'):
        p.unwrap()  # Remove the <p> tag but keep its content
    return str(soup)


def extract_container_content(soup):
    container = soup.find('div', class_='container')
    if container:
        return str(container)
    return ""


def extract_sections(soup):
    container = soup.find('div', class_='container')
    if not container:
        return []

    sections = []
    current_section = {'title': '', 'text': '', 'images': [], 'audio': []}
    for element in container.descendants:
        if element.name == 'h1':
            current_section['title'] = element.get_text(strip=True)
        elif element.name == 'h2':
            if current_section['text'] or current_section['images'] or current_section['audio']:
                sections.append(current_section)
            current_section = {'title': element.get_text(strip=True), 'text': '', 'images': [], 'audio': []}
        elif element.name == 'figure':
            img_tag = element.find('img')
            figcaption_tag = element.find('figcaption')
            if img_tag and figcaption_tag:
                img_url = "https://centrala.ag3nts.org/dane/" + img_tag['src']
                response = requests.get(img_url)
                response.raise_for_status()
                img_file_path = f"{file_path}/{os.path.basename(img_url)}"
                with open(img_file_path, 'wb') as img_file:
                    img_file.write(response.content)
                with open(img_file_path, 'rb') as img_file:
                    content = base64.b64encode(img_file.read()).decode('utf-8')
                    description = AIService().describeImage(content)
                current_section['text'] += f"Image (caption: {figcaption_tag.get_text(strip=True)}): {description} "
        elif element.name == 'audio' and 'controls' in element.attrs:
            source_tag = element.find('source')
            if source_tag and 'src' in source_tag.attrs:
                audio_url = "https://centrala.ag3nts.org/dane/" + source_tag['src']
                response = requests.get(audio_url)
                response.raise_for_status()
                audio_file_path = f"{file_path}/{os.path.basename(audio_url)}"

                with open(audio_file_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                with open(audio_file_path, 'rb') as audio_file:
                    transcription = AIService().transcribe(audio_file)
                current_section['text'] += f"Audio transcription: {transcription} "
        elif element.string:
            current_section['text'] += element.string.strip() + ' '
    if current_section['text'] or current_section['images'] or current_section['audio']:
        sections.append(current_section)
    return sections


def build_context(sections):
    context = PROMPT
    for section in sections:
        context += f"Section: {section['title']}\n"
        context += " ".join(section['text']) + "\n"
    return context


load_dotenv()
questions = retrieve_questions()
article = retrieve_article()
soup = BeautifulSoup(article, 'html.parser')

article = strip_p_tags(soup)
article = extract_container_content(soup)
print(article)

sections = extract_sections(soup)
context = build_context(sections)
answers = AIService().answer(questions, context)

print(questions)
print(answers)

response_data = verify_task(
    "arxiv", json_loads(answers), os.environ.get("aidevs.report_url"))
print(response_data)
