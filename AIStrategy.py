from abc import ABC, abstractmethod

from AIService import AIService


class AIStrategy(ABC):
    _aiservice = AIService()

    def __init__(self, medium: str) -> None:
        self.medium = medium

    @abstractmethod
    def convert(self, file: str):
        pass

    def medium(self) -> str:
        return self.medium
