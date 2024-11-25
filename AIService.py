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
        DALLE3 = "openai:dall-e-3"
        WHISPER = "openai:whisper-1"
        LLAMA32 = "ollama:llama3.2"
        GEMMA2 = "ollama:gemma2"
        SONNET3 = "anthropic:claude-3-sonnet-20240229"
        SONNET35 = "anthropic:claude-3-5-sonnet-20241022"
        HAIKU3 = "anthropic:claude-3-haiku-20240307"
        HAIKU35 = "anthropic:claude-3-5-haiku-20241022"

    PROMPT = "You are helpful assistant that can answer questions and help with tasks."
    IMG_QUESTION = "What is in the image?"
    MAX_TOKENS = 1024
    TEMPERATURE = 0
    IMG_TYPE_JPEG = "jpeg"
    IMG_TYPE_PNG = "png"

    def __init__(self, ):
        self._openai_client = OpenAI(api_key=os.environ.get("openai.api_key"))
        self._anthropic_client = anthropic.Anthropic(api_key=os.environ.get("anthropic.api_key"))

    def answer(self, question, prompt=PROMPT, model=AIModel.DEFAULT, max_tokens=MAX_TOKENS,
               temperature=TEMPERATURE) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.answerOpenAI(question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "ollama":
            return self.answerOllama(question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "anthropic":
            return self.answerAnthropic(question, prompt, aitype[1], max_tokens, temperature)
        raise ValueError(f"Unsupported AI model type: {aitype[0]}")

    def transcribe(self, audio_file, model=AIModel.WHISPER) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.transcribeOpenAI(audio_file, aitype[1])
        raise ValueError(f"Unsupported AI model type: {aitype[0]}")

    def describeImage(self, image_data, data_type=IMG_TYPE_PNG, question=IMG_QUESTION, prompt=PROMPT,
                      model=AIModel.DEFAULT,
                      max_tokens=1024,
                      temperature=0) -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.describeImageOpenAI(image_data, data_type, question, prompt, aitype[1], max_tokens, temperature)
        if aitype[0] == "anthropic":
            return self.describeImageAnthropic(image_data, data_type, question, prompt, aitype[1], max_tokens,
                                               temperature)
        raise ValueError(f"Unsupported AI model type: {aitype[0]}")

    def generateImage(self, prompt, model=AIModel.DALLE3, size="1024x1024", quality="standard") -> str:
        aitype = model.value.split(":")
        if aitype[0] == "openai":
            return self.generateImageOpenAI(prompt, aitype[1], size, quality)
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

    def answerAnthropic(self, question, prompt, model, max_tokens=MAX_TOKENS, temperature=TEMPERATURE) -> str:
        message = self._anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt,
            messages=[
                {
                    "role": "user", "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image_media_type",
                            "data": "image_data"
                        }
                    },
                    {
                        "type": "text", "text": "What is this image?"
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

    def describeImageOpenAI(self, image_data, data_type, question, prompt, model, max_tokens=None,
                            temperature=None) -> str:

        completion = self._openai_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/${data_type};base64,${image_data}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]}
            ])
        text = completion.choices[0].message.content.strip()
        return text

    def describeImageAnthropic(self, image_data, data_type, question, prompt, model, max_tokens=MAX_TOKENS,
                               temperature=TEMPERATURE) -> str:
        message = self._anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=prompt,
            messages=[
                {
                    "role": "user", "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/${data_type}",
                            "data": image_data
                        }
                    },
                    {
                        "type": "text", "text": question
                    }
                ]}
            ])
        text = message.content[0].text.strip()
        return text

    def generateImageOpenAI(self, prompt, model, size="1024x1024", quality="standard") -> str:
        response = self._openai_client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        image_url = response.data[0].url
        return image_url
