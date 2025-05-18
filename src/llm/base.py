from abc import ABC, abstractmethod

class LLM(ABC):
    def __init__(self, config:dict, model_name:str="base"):
        self.model_name = model_name
        self.config = config

    @abstractmethod
    def chat(self, history: list) -> str:
        pass

    def __str__(self):
        return f"{self.__class__.__name__} (model_name={self.model_name})"
