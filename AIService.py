import os
from enum import Enum

import anthropic
import ollama
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class AIService:
    class AIModel(Enum):
        DEFAULT = os.environ.get("openai.model")
        GPT4o = "openai:gpt-4o"
        GPT4oMINI = "openai:gpt-4o-mini"
        WHISPER = "openai:whisper-1"
        LLAMA32 = "ollama:llama3.2"
        GEMMA2 = "ollama:gemma2"
        SONNET3 = "anthropic:claude-3-sonnet-20240229"
        SONNET35 = "anthropic:claude-3-5-sonnet-20241022"
        HAIKU3 = "anthropic:claude-3-haiku-20240307"
        HAIKU35 = "anthropic:claude-3-5-haiku-20241022"

    PROMPT = "You are helpful assistant. Provide answer to the given questions."

    def __init__(self, ):
        self._openai_client = OpenAI(api_key=os.environ.get("openai.api_key"))
        self._anthropic_client = anthropic.Anthropic(api_key=os.environ.get("anthropic.api_key"))

    def answer(self, question, prompt=PROMPT, model=AIModel.DEFAULT, max_tokens=None, temperature=None) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.answerOpenAI(question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "ollama":
            return self.answerOllama(question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "anthropic":
            return self.answerAnthropic(question, prompt, aitype[1], max_tokens, temperature)
        raise ValueError(f"Unsupported AI model type: {aitype[0]}")

    def transcribe(self, file, model=AIModel.WHISPER) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.transcribeOpenAI(file, aitype[1])
        raise ValueError(f"Unsupported AI model type: {aitype[0]}")

    def answerOpenAI(self, question, prompt, model, max_tokens=None, temperature=None) -> str:
        completion = self._openai_client.chat.completions.create(
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
        completion = ollama.chat(
            model=model,
            options={
                'temperature': temperature,
                'num_ctx': max_tokens},
            messages=[{
                'role': 'system',
                'content': prompt,
            }, {'role': 'user', 'content': question}]
        )
        text = completion.get('message').get('content')
        return text

    def answerAnthropic(self, question, prompt, model, max_tokens=1000, temperature=0) -> str:
        message = self._anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt,
            messages=[
                {
                    "role": "user", "content": [
                    {
                        "type": "text", "text": question
                    }
                ]}
            ])
        text = message.content[0].text.strip()
        return text

    def transcribeOpenAI(self, audio_file, model) -> str:
        transcription = self._openai_client.audio.transcriptions.create(
            model=model,
            file=audio_file
        )
        return transcription.text
