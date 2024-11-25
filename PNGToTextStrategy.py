import base64

from AIService import AIService
from AIStrategy import AIStrategy

IMG_PROMPT = """You are helpful text recognition specialist that provides a summary of the recognized content.
  """


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
