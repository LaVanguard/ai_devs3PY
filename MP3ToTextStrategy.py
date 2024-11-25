from AIStrategy import AIStrategy


class MP3ToTextStrategy(AIStrategy):

    def __init__(self):
        super().__init__('.mp3')

    def convert(self, file: str) -> str:
        with open(file, 'rb') as f:
            return self._aiservice.transcribe(f)
