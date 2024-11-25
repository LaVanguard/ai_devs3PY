from AIStrategy import AIStrategy


class TXTToTextStrategy(AIStrategy):
    def __init__(self):
        super().__init__('.txt')

    def convert(self, file: str) -> str:
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
