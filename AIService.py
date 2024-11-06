import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIService:
    PROMPT = "You are helpful assistant. Provide answer to the given questions."
    MODEL = os.environ.get("openai.model")

    def __init__(self):
        self._client = OpenAI(api_key=os.environ.get("openai.api_key"))

    def answer(self, question, prompt=PROMPT, model=MODEL, max_tokens=None, temperature=None) -> str:
        completion = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ])
        text = completion.choices[0].message.content.strip()
        return text
