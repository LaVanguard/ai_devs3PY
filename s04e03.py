import json
import os
import uuid

from deepdiff.serialization import json_loads, json_dumps
from dotenv import load_dotenv

from AIService import AIService
from messenger import get_file_text, get_markdown, verify_task

load_dotenv()

QUESTION_PROMPT = """
<input>
{"question": "sample question", "keywords": "example keywords content"}
<input>

You are a helpful assistant.
Prepare result in the JSON format. 
_thinking:
Think twice before you provide answer. It is important to provide accurate information. Do not answer if you feel the information is not correct.
<rules>
- If there is a question in the input, provide concise answer in the output, for example when asked for URL, provide only URL.
- Make sure you provide correct URL as an answer, for instance if asked about website interface address, make sure you provide correct interface URL that is not a link to portfolio.
- NEVER provide answer if you cannot find it in the text. Do not create attribute 'answer' in such a case.
- NEVER include explanations or text outside the JSON structure
</rules>

<sample_outputs>
{"answer": "answer to the question from input"}
{"no_answer": "There is insufficient information to answer the question."}
</sample_outputs>
"""

LINKS_PROMPT = """
<input>
{"url": "https://example.com", "content": "example keywords content"}}
<input>
You are a helpful assistant.
Your job is to extract all urls that are in the given markdown content and provide brief summary of the content.
Prepare result in the JSON format. 
<rules>
- For each extracted url provide brief summary in Polish what the content is about.
- Convert urls to absolute urls by prepending them with the base url.
- NEVER include explanations or text outside the JSON structure
</rules>

<sample_outputs>
{"links": [{"url": "https://example.com", "summary": "A sample web page"}, {"url": "https://example.com/site", "summary": "A sample site"}]}
{"links": [{"url": "https://wikipedia.org/article", "summary": "Wikipedia article page"}]}
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
answer the question as best as possible. Provide the correct url as the output.
"""


SUMMARY_PROMPT = """You are an experience analyst. Analyze the given text and provide the most important information.
Focus on the specific facts, avoid general terms.
<rules>
- Be specific and concise - provide summary with the most important information.
- IMPORTANT: Pay attention to details and avoid general terms.
- Focus on specific facts.
- Collect all the urls.
- Use Polish language
</rules>
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
    file_name = os.environ.get("aidevs.s04e03.file_name")
    file_path = os.path.join(get_working_dir(), file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        json_text = json_loads(get_file_text(file_name, True))
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(json_text, file, ensure_ascii=False, indent=2)
        return json_text


def suggest_url(unique_links, visited) -> str:
    prompt = url_suggestion_prompt(unique_links, visited)
    answer_url = service.answer(value, prompt)
    print(answer_url)
    return answer_url


def retrieve_keywords(url: str) -> str:
    directory = get_working_dir()
    file_content = retrieve_file(url, directory)

    if file_content:
        return file_content
    else:
        markdown = get_markdown(url)
        keywords = service.answer(markdown, SUMMARY_PROMPT)
        store_file(url, keywords, directory)
        return keywords


def retrieve_links(url, keywords, links):
    context = json_dumps({"url": url, "content": keywords})
    answer = json_loads(service.answer(context, LINKS_PROMPT))
    print(answer)
    if "links" in answer:
        update_links(answer, links)


def update_links(context, links):
    for link in context["links"]:
        links[link["url"]] = link["summary"]


base_url = os.environ.get("aidevs.s04e03.url")
service = AIService()
keywords = retrieve_keywords(base_url)

data = retrieve_data()
answers = {}
visited = set()
input_url = json_dumps({"url": base_url, "keywords": keywords})
unique_links = {}
retrieve_links(input_url, keywords, unique_links)


def answer_question(question, keywords) -> str:
    input_data = json_dumps({"question": question, "content": keywords})
    answer = json_loads(service.answer(input_data, QUESTION_PROMPT, model=AIService.AIModel.SONNET35))
    print(answer)
    return answer


for key, value in data.items():
    visited.clear()
    links_to_visit = unique_links.copy()
    while links_to_visit:
        answer_url = suggest_url(unique_links, visited)
        keywords = retrieve_keywords(answer_url)
        retrieve_links(answer_url, keywords, unique_links)
        answer = answer_question(value, keywords)
        if "answer" in answer:
            answers[key] = answer["answer"]
            break
        links_to_visit.pop(answer_url)
response_data = verify_task("softo", answers)
