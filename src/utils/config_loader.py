import json
import yaml
import os

class ConfigLoader:
    """support json, yaml file"""
    def __init__(self):
        pass
    
    def get_config_from_file(self, path:str) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File không tồn tại: {path}")
        
        if path.endswith('.json'):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif path.endswith(".yaml") or path.endswith(".yml"):
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {path}")
        
if __name__ == "__main__":
    cfg = ConfigLoader().get_config_from_file(r"E:\src code 2\python 2\Legal_RAG\config\config.yaml")
    print(cfg)