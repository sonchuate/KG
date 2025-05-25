from src.llm.base import LLM
from src.db.neo4j import (Node, Edge)
from typing import List, Tuple
from src.prompt.index import (
    GRAPH_EXTRACTION_PROMPT_v0,
    INCLUDE_RELATIONSHIP_EXTRACTION_PROMPT,
    CV_EXTRACT_GRAPH_PROMPT,
    JD_EXTRACT_GRAPH_PROMPT,
    SUMMERIZE_CV_PROMPT,
    SUMMERIZE_JD_PROMPT
)
from src.index.utils import cal_exp
import json
import os

class Entity:
    def __init__(self, entity_name:str, entity_type:str, entity_description:str):
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.entity_description = entity_description
    
    def node(self) -> Node:
        return Node(label=self.entity_type, properties={"name" : self.entity_name})
    
    def show(self):
        print(f'Entity -- entity_name {self.entity_name} -- entity_type {self.entity_type} -- entity_description {self.entity_description}')

class Relationship:
    def __init__(self, source_entity:str, target_entity:str, relationship_description:str):
        self.source_entity = source_entity
        self.target_entity = target_entity
        self.relationship_description = relationship_description

    def show(self):
        print(f'Relationship -- source_entity {self.source_entity} -- target_entity {self.target_entity} -- relationship_description {self.relationship_description}')

class EntityExtractor:
    """
    format bắt buộc là 
    ("entity"<|><entity_name><|><entity_type><|><entity_description>)
    ("relationship"<|><source_entity><|><target_entity><|><relationship_description><|><relationship_strength>)
    một số trường có thể thiếu nhưng số lượng <|> nên là đủ
    """
    def __init__(self, entities:str, llm:LLM, cache_folder:str="cache"):
        self.llm = llm
        self.entities = entities
        self.cache_folder = cache_folder
        os.makedirs(cache_folder, exist_ok=True)

    def get_entities_default(self, input_text:str, log_file_name:str="") -> Tuple[List[Entity], List[Relationship]]:
        response = self.llm.chat([{'role':'user','content':GRAPH_EXTRACTION_PROMPT_v0.format(entity_types=self.entities, input_text=input_text)}])

        if log_file_name != "":
            with open(f'{self.cache_folder}/{log_file_name}', 'w', encoding='utf-8') as f:
                f.write(response)

        return self.parse_entities(response)

    def get_entities_include(self, input_text:str, log_file_name:str="") -> Tuple[List[Entity], List[Relationship]]:
        response = self.llm.chat([{'role':'user','content':INCLUDE_RELATIONSHIP_EXTRACTION_PROMPT.format(entity_types=self.entities, input_text=input_text)}])

        if log_file_name != "":
            with open(f'{self.cache_folder}/{log_file_name}', 'w', encoding='utf-8') as f:
                f.write(response)

        return self.parse_entities(response)

    def parse_entities(self, response:str) -> Tuple[List[Entity], List[Relationship]]:
        entities_list = []
        relationship_list = []
        for line in response.split('\n'):
            line = line.strip().strip('(').strip(')')
            if line.startswith('"entity"'):
                _, entity_name, entity_type, entity_description = line.split('<|>')[:4]
                entities_list.append(Entity(entity_name, entity_type, entity_description))
            if line.startswith('"relationship"'):
                _, source_entity, target_entity, relationship_description = line.split('<|>')[:4]
                relationship_list.append(Relationship(source_entity, target_entity, relationship_description))
        return entities_list, relationship_list
    
    def get_entities_from_cv(self, cv:str, entity_types:str="", log_file_name:str="") -> Tuple[list[Entity], float]:
        if entity_types == "":
            entity_types = self.entities

        summerize_cv = self.llm.chat([
            {'role':'user','content':SUMMERIZE_CV_PROMPT.format(cv= cv)}
            
        ])
        
        exp = 0
        try:
            skill, exp_text = summerize_cv.split("##")
            skill = skill.split('```json')[1].split('```')[0]
            exp_text = exp_text.split('```json')[1].split('```')[0]

            skill = json.loads(skill)["skill"]
            exp_list = json.loads(exp_text)
            for e in exp_list:
                exp += cal_exp(e["start_time"], e["end_time"])
        except:
            print('!!Exception when process cv')
            return [], 0


        response = self.llm.chat([
            {'role':'user','content':CV_EXTRACT_GRAPH_PROMPT.format(entity_types=entity_types ,  input_text= skill)}
            
        ])

        if log_file_name != "":
            with open(f'{self.cache_folder}/{log_file_name}', 'w', encoding='utf-8') as f:
                f.write(response)

        entities_list, relationship_list = self.parse_entities(response)
        return entities_list, exp
    
    def get_entities_from_jd(self, jd:str, entity_types:str="", log_file_name:str="") -> Tuple[list[Entity], float]:
        if entity_types == "":
            entity_types = self.entities

        summerize_jd = self.llm.chat([
            {'role':'user','content':SUMMERIZE_JD_PROMPT.format(jd = jd)}
            
        ])
        print('summerize_jd', summerize_jd)
        requirements = ""
        exp = 0
        try:
            for entity in summerize_jd.split("##"):
                entity = entity.strip('\n').strip()
                if entity == 0: continue
                
                if entity.lower().startswith('requires'):
                    requirements = entity
                elif entity.lower().startswith('degree'):
                    """to do: process degree"""
                    pass
                elif entity.lower().startswith('place'):
                    requirements += "\n" + entity
                elif entity.lower().startswith('exp'):
                    exp = float(entity.split(':')[1])
        except:
            print('!!Exception when process jd')
            return [], 0


        response = self.llm.chat([
            {'role':'user','content':JD_EXTRACT_GRAPH_PROMPT.format(entity_types=entity_types ,  input_text= requirements)}
            
        ])
        
        if log_file_name != "":
            with open(f'{self.cache_folder}/{log_file_name}', 'w', encoding='utf-8') as f:
                f.write(response)

        entities_list, relationship_list = self.parse_entities(response)
        return entities_list, exp    

if __name__ == "__main__":
    from src.utils.config_loader import ConfigLoader
    from src.llm.gemini import Gemini_LLM

    config = ConfigLoader().get_config_from_file(r"E:\src code 2\python 2\Legal_RAG\config\config.yaml")
    llm = Gemini_LLM(config=config)
    entity_extractor = EntityExtractor(entities="Person, Job", llm=llm)
    entities_list, relationship_list = entity_extractor.get_entities_include("Cao Sơn is an AI engineer", 'log.txt')

    