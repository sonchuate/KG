from src.llm.base import LLM
import json
import requests as rq

class Gemini_LLM(LLM):
    def __init__(self, config):
        super().__init__()
        self.model_name = config.get('model_name', 'gemini-1.5-flash')
        self.gemini_key = config.get('gemini_key', '')
        if self.gemini_key == "":
            raise ValueError("Please add gemini_key in config file!")
        
    def create_assistant_chat(self, message:str) -> dict:
        return {"role": "model", "parts": [{"text": message}]}
    
    def create_user_chat(self, message:str) -> dict:
        return {"role": "user", "parts": [{"text": message}]}

    def request(self, key:str, chat_history:list) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key}"
        payload = json.dumps({"contents": chat_history})
        headers = {"Content-Type": "application/json"}
        response = rq.post(url, headers=headers, data=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def chat(self, history:list) -> str:
        chat_history = []
        for item in history:
            role = item['role']
            message = item['content']
            if role == 'assistant':
                chat_history.append(self.create_assistant_chat(message))
            if role == 'user':
                chat_history.append(self.create_user_chat(message))
            else:
                raise ValueError("role không xác định: " + role)
            
        if isinstance(self.gemini_key, list):
            rs = "Hết quota"
            for key in self.gemini_key:
                try:
                    return self.request(key, chat_history)
                except:
                    pass
        
            return rs
        
        return self.request(self.gemini_key, chat_history)
        
if __name__ == "__main__":
    config = {'gemini_key':[
            ]}
    llm  = Gemini_LLM(config)
    print(llm.chat([{'role':'user','content':'How are you today'}]))

        