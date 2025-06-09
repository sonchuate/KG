from src.llm.base import LLM
from src.prompt.chatbot import ROUTE_INTRUCTION

class Conversation:
    def __init__(self, llm:LLM):
        self.llm = llm
        self.history = []
        self.cv = None
        self.jd = None

    def route(self, text:str, list_job:str):
        response = self.llm.chat([
            {'role':'user','content':ROUTE_INTRUCTION.format(list_job= list_job, text=text)}
        ])
        return response

    def chat(self, text:str) -> str:
        ans = self.history.append(
            {'role':'user','content':text}
        )
        
        self.history.append(
            {'role':'assistant','content':ans}
        )

        return ans