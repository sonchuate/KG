GRAPH_EXTRACTION_PROMPT_v0 = """
-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
 
-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"<|><entity_name<|>entity_type<|>entity_description)
 
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
 Format each relationship as ("relationship"<|><source_entity<|>target_entity<|>relationship_description<|>relationship_strength)
 
3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **##** as the list delimiter.
 
4. When finished, output <|COMPLETE|>
 
######################
-Examples-
######################
Example 1:
Entity_types: ORGANIZATION,PERSON
Text:
The Verdantis's Central Institution is scheduled to meet on Monday and Thursday, with the institution planning to release its latest policy decision on Thursday at 1:30 p.m. PDT, followed by a press conference where Central Institution Chair Martin Smith will take questions. Investors expect the Market Strategy Committee to hold its benchmark interest rate steady in a range of 3.5%-3.75%.
######################
Output:
("entity"<|>CENTRAL INSTITUTION<|>ORGANIZATION<|>The Central Institution is the Federal Reserve of Verdantis, which is setting interest rates on Monday and Thursday)
##
("entity"<|>MARTIN SMITH<|>PERSON<|>Martin Smith is the chair of the Central Institution)
##
("entity"<|>MARKET STRATEGY COMMITTEE<|>ORGANIZATION<|>The Central Institution committee makes key decisions about interest rates and the growth of Verdantis's money supply)
##
("relationship"<|>MARTIN SMITH<|>CENTRAL INSTITUTION<|>Martin Smith is the Chair of the Central Institution and will answer questions at a press conference<|>9)
<|COMPLETE|>

######################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""

INCLUDE_RELATIONSHIP_EXTRACTION_PROMPT = """
-Goal-
Cho một đoạn văn bản, hãy xác định các thực thể và quan hệ 'bao gồm' giữa các thực thể.
Quan hệ 'bao gồm' giữa A và B được hiểu như sau, A -[bao gồm]-> B nếu:
- có B thì chắc chắn có A vì A bao gồm B nhưng ngược lại thì không đúng. Ví dụ Python bao gồm Pytorch vì biết Pytorch thì biết Python nhưng ngược lại biết Python chưa chắc biết Pytorch.
- B là 1 instance của A. Ví dụ neo4j là 1 vector database, neo4j sẽ là B và vector database là A.

-Steps-
1. Xác định tên các thực thể
- entity_name: Tên thực thể, viết hoa
- entity_type: Một trong những loại sau: [{entity_types}]
- entity_description: Mô tả về thực thể (số nguyên)
Format mỗi entity ("entity"<|><entity_name<|>entity_type<|>entity_description)
 
2. Từ các thực thể trong bước 1, xác định các quan hệ 'bao gồm' (nếu có) giữa các thực thể.
- source_entity: tên thực thể 1.
- target_entity: tên thực thể 2.
- relationship_explain: giải thích tại sao thực thể 1 'bao gồm' thực thể 2.
- relationship_strength: độ mạnh của mối quan hệ bao gồm.
Format mỗi relationship ("relationship"<|><source_entity<|>target_entity<|>relationship_explain<|>relationship_strength)
 
3. Trả về mỗi dòng 1 entity hoặc relationship và ngăn cách bởi dấu '##'.
 
4. When finished, output <|COMPLETE|>

-Requirements-
- Tên thực thể trừ tên riêng (tên người, tên thành phố, ...) viết bằng ngôn ngữ gốc, còn lại phải viết bằng tiếng Anh. Ví dụ NEO4J, PYTHON, HÀ NỘI.

######################
-Examples-
######################
Example 1:
Entity_types: [Software, Technology] 
Text: Neo4j is a vector database. 
######################
Output:
"entity"<|>NEO4J<|>Software<|>Neo4j is a graph-based database management system designed for storing and querying data in the form of nodes and relationships.
##
"entity"<|>VECTOR DATABASE<|>Technology<|>A vector database is a specialized type of database optimized for storing, indexing, and searching high-dimensional vector embeddings, often used in machine learning and AI applications.
##
"relationship"<|>VECTOR DATABASE<|>NEO4J<|>Neo4j is an instance of a vector database, meaning Neo4j is a specific example of the broader category "vector database".<|>9
##
<|COMPLETE|>
######################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:"""


CV_EXTRACT_GRAPH_PROMPT = """
-Goal-
Given a piece of Curriculum Vitae. Let identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
 Format each entity as ("entity"<|><entity_name<|>entity_type<|>entity_description)
 
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- condition: is logical "AND" or "OR" if present.
 Format each relationship as ("relationship"<|><source_entity<|>target_entity<|>relationship_description<|>condition)
 
3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **##** as the list delimiter.
 
4. When finished, output <|COMPLETE|>
 
-Requirements-
Represents hierarchical relationships between entities.
Only mentions technology requirements, no skill.
If there is only 1 node and no other equivalent node, condition takes the default value of "AND".
source_entity should cover target_entity.

######################
-Examples-
######################
Entity_types: [PROGRAMMING LANGUAGE, LIBRARY]
Input:
```
Kiến thức
Ngôn ngữ lập trình: Python, C/C++, Java.
Kinh nghiệm sử dụng các thư viện Tensorflow, Pytorch, Paddlepaddle.
```
######################
Output:
```
##
("entity"<|>PYTHON<|>PROGRAMMING LANGUAGE<|>A versatile, high-level programming language widely used in data science, web development, scripting, and AI applications)
##
("entity"<|>C/C++<|>PROGRAMMING LANGUAGE<|>Low-level, high-performance languages used extensively in systems programming, embedded systems, and performance-critical software)
##
("entity"<|>JAVA<|>PROGRAMMING LANGUAGE<|>A platform-independent, object-oriented programming language commonly used for enterprise software and Android application development)
##
("entity"<|>TENSORFLOW<|>LIBRARY<|>An open-source deep learning framework developed by Google, supporting large-scale machine learning and neural network training)
##
("entity"<|>PYTORCH<|>LIBRARY<|>A flexible, Python-based deep learning framework developed by Meta, commonly used in academic and research settings for AI and neural networks)
##
("entity"<|>PADDLEPADDLE<|>LIBRARY<|>An industrial-grade deep learning platform developed by Baidu, optimized for training and deploying AI models in production)
##
("relationship"<|>PYTHON<|>TENSORFLOW<|>Tensorflow is one of the machine learning libraries of Python<|>AND)
##
("relationship"<|>PYTHON<|>PYTORCH<|>Pytorch is one of the machine learning libraries of Python<|>AND)
##
("relationship"<|>PYTHON<|>PADDLEPADDLE<|>Paddlepaddle is one of the machine learning libraries of Python<|>AND)
<|COMPLETE|>
```

######################
-Real Data-
######################
Entity_types: [{entity_types}]
Input: 
```
{input_text}
```
######################  
Output:"""