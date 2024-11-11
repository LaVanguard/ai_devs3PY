import os
from enum import Enum

import ollama
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIService:
    class AIModel(Enum):
        DEFAULT = os.environ.get("openai.model")
        GPT4o = "openai:gpt-4o"
        GPT4oMINI = "openai:gpt-4o-mini"
        LLAMA32 = "ollama:llama3.2"
        GEMMA2 = "ollama:gemma2"

    PROMPT = "You are helpful assistant. Provide answer to the given questions."

    def __init__(self):
        self._client = OpenAI(api_key=os.environ.get("openai.api_key"))

    def answer(self, question, prompt=PROMPT, model=AIModel.DEFAULT, max_tokens=None, temperature=None) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.answerOpenAI(question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "ollama":
            return self.answerOllama(question, prompt, aitype[1], max_tokens, temperature)
        return ""

    def answerOpenAI(self, question, prompt, model, max_tokens=None, temperature=None) -> str:
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

    def answerOllama(self, question, prompt, model, max_tokens=None, temperature=None) -> str:
        censored = ollama.chat(
            model=model,
            options={
                'temperature': temperature,
                'num_ctx': max_tokens},
            messages=[{
                'role': 'system',
                'content': prompt,
            }, {'role': 'user', 'content': question}]
        )
        text = censored.get('message').get('content')
        return text
