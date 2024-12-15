import json
import os
import uuid

from deepdiff.serialization import json_loads, json_dumps
from dotenv import load_dotenv

from AIService import AIService
from messenger import get_file_data, get_markdown

load_dotenv()
# {"url": "https://example.com", "title": "Example Title", "summary": "Example Content summary", "uuid": "example-uuid", "file": "example-file"}
CRAWLER_PROMPT = f"""
<input>
{{"url": "https://example.com", "question": "sample question", "markdown": "example markdown content"}}
{{"url": "https://example.com", "markdown": "example markdown content"}}
<input>

You are a helpful assistant.
Your job is to extract all relative urls that are in the given markdown content and provide brief summary of the content.
Prepare result in the JSON format. 
<rules>
- For each extracted url provide brief summary what the content is about.
- Convert urls to absolute urls by prepending them with the base url.
- If there is a question in the input, provide the answer in the output.
- Never provide answer if you don't know it
- NEVER include explanations or text outside the JSON structure
</rules>

<sample_outputs>
{{"links": [{{"url": "https://example.com", "summary": "A sample web page"}}, {{"url": "https://example.com/site", "summary": "A sample site"}}]}}
{{"answer": "answer to the question from input", "links": [{{"url": "https://wikipedia.org/article", "summary": "Wikipedia article page"}}]}}

</sample_outputs>
"""


def url_suggestion_prompt(links, visited):
    # Filter out visited URLs from the context
    filtered_links = {url: summary for url, summary in links.items() if url not in visited}
    context = {"links": filtered_links}
    return f"""
    
<context>
{context}
</context>
You are a helpful assistant. Your task is to choose the correct url from the list of suggestions in order to
answer the question. Provide the correct url as the output.
"""


QUESTION_PROMPT = """
{{"url": "https://example.com", "question": "sample question", "markdown": "example markdown content"}}
You are a helpful assistant.

Your job is to provide concise answer to the given question.
<rules>
- Your answer should be clear and concise.
- Your answer should be based on the information available on the website.
- Use as few words as possible.
</rules?
"""

WEBSITE_SUMMARY_PROMPT = f"""
   
"""

PROMPT1 = f""""
You are a helpful assistant from the SoftoAI company. You work with the SoftoAI website at {os.environ.get("aidevs.s04e03.url")}.
Browse information available at the website to answer given question. Follow links to available on the website 
"""


def get_working_dir() -> str:
    working_dir = "resources/s04e03"
    os.makedirs(working_dir, exist_ok=True)
    return working_dir


def generate_uuid(url: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, url))


def store_file(url: str, content: str, directory: str):
    file_uuid = generate_uuid(url)
    file_path = os.path.join(directory, file_uuid)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def retrieve_file(url: str, directory: str) -> str:
    file_uuid = generate_uuid(url)
    file_path = os.path.join(directory, file_uuid)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        return None


# Download the ZIP file
def retrieve_data():
    working_dir = get_working_dir()
    if len(os.listdir(working_dir)) == 0:
        file_name = os.environ.get("aidevs.s04e03.file_name")
        json_text = json_loads(get_file_data(file_name, True))
        file_path = os.path.join(get_working_dir(), file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_text, file, ensure_ascii=False, indent=2)
        return json_text
    else:
        with open(os.path.join(working_dir, os.environ.get("aidevs.s04e03.file_name")), 'r', encoding='utf-8') as file:
            return json.load(file)


def retrieve_markdown(url: str) -> str:
    directory = get_working_dir()
    file_content = retrieve_file(url, directory)

    if file_content:
        return file_content
    else:
        markdown = get_markdown(url)
        store_file(url, markdown, directory)
        return markdown


base_url = os.environ.get("aidevs.s04e03.url")
service = AIService()
markdown = retrieve_markdown(base_url)

data = retrieve_data()
answers = {}
visited = set()
input_url = json_dumps({"url": base_url, "markdown": markdown})
context = json_loads(service.answer(input_url, CRAWLER_PROMPT))
print(context)
unique_links = {}
for link in context["links"]:
    unique_links[link["url"]] = link["summary"]

for key, value in data.items():
    print(f"Question {key}: {value}")
    visited.clear()
    while unique_links:
        prompt = url_suggestion_prompt(unique_links, visited)
        answer_url = service.answer(value, prompt)
        print(answer_url)
        visited.add(answer_url)
        markdown = retrieve_markdown(answer_url)
        input_data = json_dumps({"url": answer_url, "question": value, "markdown": markdown})
        answer = json_loads(service.answer(input_data, CRAWLER_PROMPT))
        print(answer)
        if "answer" in answer:
            answers[key] = answer["answer"]
            break
        if "links" in answer:
            for link in answer["links"]:
                unique_links[link["url"]] = link["summary"]

# webService = WebSearchService()
# markdown = webService.scrape_url("https://softo.ag3nts.org/")

# print(markdown)
#
# file_id = upload_fine_tuning_file()
# fine_tune_job_id = create_fine_tuning_job(file_id)
#
# {
#   "01": "Podaj adres mailowy do firmy SoftoAI",
#   "02": "Jaki jest adres interfejsu webowego do sterowania robotami zrealizowanego dla klienta jakim jest firma BanAN?",
#   "03": "Jakie dwa certyfikaty jakości ISO otrzymała firma SoftoAI?"
# }
# answer = {"01": "kontakt@softoai.whatever", "02": "https://banan.ag3nts.org/", "03": "03-ISO 9001 oraz ISO/IEC 27001"}
# response_data = verify_task("softo", answer)
# print(response_data)
