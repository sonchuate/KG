from src.llm.base import LLM
import json
import requests as rq

class vLLM_LLM(LLM):
    def __init__(self, config):
        super().__init__(config)
        self.model_name = config.get('model_name', "Qwen/Qwen2.5-7B-Instruct")
        self.url = config.get('url', "") + "/v1/chat/completions"
        if self.url == "/v1/chat/completions":
            raise ValueError("Please add url in config file!")
        
    def create_assistant_chat(self, message:str) -> dict:
        return {"role": "assistant", "content": message}
    
    def create_user_chat(self, message:str) -> dict:
        return {"role": "user", "content": message}
    
    def create_system_chat(self, message:str) -> dict:
        return {"role": "system", "content": message}
    
    def chat(self, history:list) -> str:
        chat_history = []
        for item in history:
            role = item['role']
            message = item['content']
            if role == 'assistant':
                chat_history.append(self.create_assistant_chat(message))
            elif role == 'user':
                chat_history.append(self.create_user_chat(message))
            elif role == 'system':
                chat_history.append(self.create_system_chat(message))
            else:
                raise ValueError("role không xác định: " + role)
        payload = json.dumps({
            "model": self.model_name,
            "messages": chat_history}
        )
        headers = {"Content-Type": "application/json"}
        response = rq.post(self.url, headers=headers, data=payload)
        try:
            return response.json()['choices'][0]['message']['content']
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
        
if __name__ == "__main__":
    import time
    """chạy https://www.kaggle.com/code/sontrancao/vllm-serve-qwen-2-5-7b trước để có llm api"""
    llm  = vLLM_LLM({'url':'https://cb3d-35-196-15-143.ngrok-free.app'})
    st = time.time()
    print(llm.chat([
        {'role':'system','content':'You are assistant'},
        {'role':'user','content':'How are you today'}
        
    ]))
    print('/> exec time:', time.time() - st)

        