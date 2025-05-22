from src.llm.base import LLM
from src.db.neo4j import (Node, Edge)
from typing import List, Tuple
from src.prompt.index import (
    GRAPH_EXTRACTION_PROMPT_v0
)
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
            with open(f'{self.cache_folder}/{log_file_name}', 'w') as f:
                f.write(response)

        return self.parse_entities(response)

    def parse_entities(self, response:str) -> Tuple[List[Entity], List[Relationship]]:
        entities_list = []
        relationship_list = []
        for line in response.split('\n'):
            line = line.strip().strip('(').strip(')')
            if line.startswith('"entity"'):
                _, entity_name, entity_type, entity_description = line.split('<|>')
                entities_list.append(Entity(entity_name, entity_type, entity_description))
            if line.startswith('"relationship"'):
                _, source_entity, target_entity, relationship_description, relationship_strength = line.split('<|>')
                relationship_list.append(Relationship(source_entity, target_entity, relationship_description))
        return entities_list, relationship_list
if __name__ == "__main__":
    from src.utils.config_loader import ConfigLoader
    from src.llm.gemini import Gemini_LLM

    config = ConfigLoader().get_config_from_file(r"E:\src code 2\python 2\Legal_RAG\config\config.yaml")
    llm = Gemini_LLM(config=config)
    entity_extractor = EntityExtractor(entities="Person, Job", llm=llm)
    entities_list, relationship_list = entity_extractor.get_entities_default("Cao Son is an AI engineer")
    for entity in entities_list:
        entity.show()
    