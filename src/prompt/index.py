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

INCLUDE_RELATIONSHIP_EXTRACTION_PROMPT_v0 = """Goal: Xác định các thực thể và mối quan hệ bao gồm giữa chúng.

Step:
1. Xác định các thực thể.
format: entity<|><tên thực thể><|>

2. Mối quan hệ bao gồm. 
- Hãy tưởng tượng bạn là một kĩ sư, nếu bạn có kĩ năng là entity_2 thì bạn chắc chắn phải có kĩ năng entity_1 vì entity_1 bao gồm kĩ năng entity_2. Ví dụ DevOps bao gồm MLOps vì biết MLOps sẽ có kĩ năng của DevOps còn ngược lại không đúng.
- Đối với phần mềm hay thư viện. entity_1 sẽ chứa entity_2 hay nói cách khác entity_2 là 1 phần của entity_1.  Ví dụ entity_2 là một thư viện của entity_1.
- entity_2 có thể là 1 instance của entity_1. Ví dụ neo4j is a vector database. 'neo4j' là entity_2 và 'vector database' là entity_1.
Mối quan hệ bao gồm sẽ là entity_1 -[include]-> entity_2. 
format: relationship<|><name1><|><name2><|>

3. Giữa các thực thể và quan hệ ngăn cách bởi dấu: ##

Requirements
Chỉ trả về kết quả, không lập luận hay chat chit.
Tên thực thể không nên chứa các từ chung chung ví dụ: "library", "interface", "application", ...
Tên thực thể viết hoa, giữ dấu cách. ví dụ: COMPUTER VISION
Hãy cố suy luận. Ví dụ input: "pytorch được sử dụng dưới dạng python interface", thì tương đương với python bao gồm pytorch.

Example:
Input: pytorch là một thư viện của python.
Output:
entity<|>PYTORCH<|>
##
entity<|>PYTHON<|>
##
relationship<|>PYTHON<|>PYTORCH<|>
####################
Input: {input_text}
Output: """

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


JD_EXTRACT_GRAPH_PROMPT = """
-Goal-
Given a piece of Job Description. Let identify all entities of those types from the text and include relationships among the identified entities.

-Steps-
1. Extract all entities mentioned in the job requirement. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
 Format each entity as ("entity"<|><entity_name><|><entity_type><|><entity_description>)
 
2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other. And only identify ALL INCLUDE relationship.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1.
- target_entity: name of the target entity, as identified in step 1.
- relationship_description: explanation as to why you think the source entity includes the target entity.
- condition: is logical "AND" or "OR" if present.
 Format each relationship as ("relationship"<|><source_entity><|><target_entity><|><relationship_description><|><condition>)
 
3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **##** as the list delimiter.
 
4. When finished, output <|COMPLETE|>
 
-Requirements-
- It should only include technology requirements — do not include skills.
- If there is only one node and no equivalent nodes, the logical condition defaults to "AND".
- The source_entity must logically cover or include the target_entity DIRECTLY.
Example:
Valid example: If source_entity = "python" and target_entity = "torch", this is valid because torch is a Python-based library. 
Invalid example: JAVA<|>PYTORCH<|>PyTorch can be used with Java through appropriate wrappers or integrations. JAVA can not use PyTorch directly.

######################
-Examples-
######################
Input:
Yêu cầu ứng viên
- Tốt nghiệp đại học chính quy chuyên ngành: Công nghệ thông tin, Tự động hóa, Điều khiển tự động, etc.,
- Có kinh nghiệm sử dụng một trong các ngôn ngữ lập trình C, C#, VB, Python, etc.,
- Có tinh thần tự giác học hỏi, nghiêm túc trong công việc
- Tiếng Anh: Đọc hiểu, giao tiếp
- Ưu tiên ứng viên đã có 1 năm kinh nghiệm làm việc với AIRFLOW.
- Biết đồng thời 2 thư viện torch và tenserflow.
- Làm việc tại Nam Từ Liêm, Hà Nội
######################
Output:
##
("entity"<|>CÔNG NGHỆ THÔNG TIN<|>MAJOR<|>A university major focused on computing, programming, systems analysis, and IT infrastructure.)
##
("entity"<|>TỰ ĐỘNG HÓA<|>MAJOR<|>A university major dealing with automation technology, including sensors, control systems, and industrial robotics.)
##
("entity"<|>ĐIỀU KHIỂN TỰ ĐỘNG<|>MAJOR<|>A university major that focuses on control engineering, systems automation, and real-time systems.)
##
("entity"<|>C<|>PROGRAMMING LANGUAGE<|>A general-purpose, procedural programming language used for system and application development.)
##
("entity"<|>C#<|>PROGRAMMING LANGUAGE<|>A modern, object-oriented programming language developed by Microsoft for building various types of applications.)
##
("entity"<|>VB<|>PROGRAMMING LANGUAGE<|>A high-level programming language from Microsoft known as Visual Basic, primarily used for Windows application development.)
##
("entity"<|>PYTHON<|>PROGRAMMING LANGUAGE<|>A high-level, interpreted language known for its readability and wide use in data science, AI, and web development.)
##
("entity"<|>TORCH<|>LIBRARY<|>An open-source machine learning library used for deep learning, built on the Lua programming language.)
##
("entity"<|>TENSORFLOW<|>LIBRARY<|>An open-source machine learning library developed by Google for deep learning and numerical computation.)
##
("entity"<|>TIẾNG ANH<|>LANGUAGE<|>The English language, required for reading comprehension and verbal communication.)
##
("entity"<|>AIRFLOW<|>SOFTWARE<|>An open-source platform for programmatically authoring, scheduling, and monitoring workflows.)
##
("entity"<|>NAM TỪ LIÊM<|>DISTRICT<|>An urban district of Hanoi, Vietnam, where the job location is specified.)
##
("entity"<|>HÀ NỘI<|>CITY<|>The capital city of Vietnam, where Nam Từ Liêm is located.)
##
("entity"<|>1 NĂM KINH NGHIỆM<|>EXPERIENCE<|>Refers to having one year of professional experience, which is considered a preference for candidates.)
##
("relationship"<|>PYTHON<|>TORCH<|>Torch is a machine learning library often used in Python-based environments.<|>AND)
##
("relationship"<|>PYTHON<|>TENSORFLOW<|>TensorFlow is a Python-compatible library used for deep learning and numerical computing.<|>AND)
##
("relationship"<|>HÀ NỘI<|>NAM TỪ LIÊM<|>Nam Từ Liêm is a district located within the city of Hà Nội.<|>AND)

<|COMPLETE|>
######################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################  
Output:"""

SUMMERIZE_CV_PROMPT = """
-Goals-
Trích xuất kĩ năng, kiến thức, công nghệ; trích xuất kinh nghiệm làm việc trong CV sau.
-Steps-
1. Trích xuất đoạn text nói về kĩ năng, kiến thức, công nghệ(skill, knowledge, technical) được viết trong CV, nó có thể là mục skill hay mục khác.
format: 
```json
{{
  "skill": "Đoạn text nói về các skill"
}}
```

2. Trích xuất kinh nghiệm làm việc, mỗi giai đoạn/ công ty.
format:
```json
[
  {{
    "company": "company_name",
    "start_time": "mon:year",
    "end_time": "now"
  }},
  {{
    "company": "company_name",
    "start_time": "mon:year",
    "end_time": "mon:year"
  }}
]
```
Lưu ý: mon:year là tháng và năm. Nếu không xác định được tháng, mặc định là tháng 01. Nếu là thời điểm hiện tại/ bây giờ, trả về "now".
Ví dụ: 01:2024 hoặc 11:2025

3. Ngăn cách giữa 2 mục là dấu ##

-Requirements-
Chỉ trả về 2 thông tin trên mà không kèm theo suy luận hay chat chit.
####################
Bắt đầu.
CV:
```text
{cv}
```
Output:
"""

SUMMERIZE_JD_PROMPT = """
-Goal-
Rút ngắn đoạn jd bằng cách chỉ trích xuất các thông tin cần thiết.
-Steps-
1. Trích xuất đoạn văn bản là yêu cầu của ứng viên về kĩ năng, kiến thức. Trong step này, không xác định bằng cấp, kinh nghiệm làm việc.
format: Requires: ...

2. Trích xuất thông tin về bằng cấp. Riêng phần này trả về kết quả tiếng anh
format: Degree: level - major.

3. Trích xuất địa điểm làm việc. Chú ý: chỉ lấy tên thành phố và tên quận, tên nước(nếu có). Nếu công việc là remote, hãy để trống phần này.
format: Place:...

4. Trích xuất kinh nghiệm làm việc cần thiết. Để đơn vị năm, nếu không có, mặc định là 0.
formart: Exp:...
Ví dụ: Exp: 10

5. Các thông tin trên viết thành các đoạn, ngăn giữa mỗi thông tin là dấu ## viết thành dòng riêng
Ví dụ
Requires: ...
##
Degree:...
##
Place: ...
##
Exp: ...


-Requirements-
Chỉ trả về các thông tin trên, không giải thích, không chat chit.
-Start-
JD:
{jd}

Output:
"""
