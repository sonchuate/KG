from src.db.neo4j import GraphManager, Node, NodeRelation, Edge

from src.utils.type import TYPE_OF_ENTITY_IN_KG, TYPE_OF_JOB, TYPE_OF_JOB_ENTITY, TYPE_OF_CV, TYPE_OF_EDGE

def get_father_node_name(gm: GraphManager, node:Node, num_gen:int=1) -> list[Node]:
    """lấy tên của các cha cách node <= num_gen thể hệ"""
    label = node.label
    
    relations_to_node = gm.get_relations_to_node(node)
    tmp = [n.node.properties["name"] for n in relations_to_node]
    parent_node_name = tmp.copy()
    num_gen -= 1

    while num_gen and tmp:
        new_tmp = []
        for node_name in tmp:
            relations_to_node = gm.get_relations_to_node(Node(label, {"name": node_name}))
            for node_relation in relations_to_node:
                neighber_node_name = node_relation.node.properties["name"]
                if neighber_node_name not in parent_node_name:
                    new_tmp.append(neighber_node_name)
            
        parent_node_name.extend(new_tmp)
        tmp = new_tmp
        num_gen -= 1

    return list(set(parent_node_name))

def get_top_similar_node(gm: GraphManager, root_node:Node, neighbor_nodes:list[Node], label:str, num_gen:int=1, top_k:int=5) -> list[str]:
    for node in neighbor_nodes:
        gm.add_edge(Edge(root_node, node, TYPE_OF_EDGE))

    for neighbor_node in neighbor_nodes:
        neighbor_node_name = node.properties["name"]
        neighbor_node = Node(TYPE_OF_ENTITY_IN_KG, {"name" : neighbor_node_name})
        for node_name in get_father_node_name(gm, neighbor_node, num_gen):
            print("father node", node_name)
            gm.add_edge(Edge(root_node, Node(TYPE_OF_JOB_ENTITY, {"name":node_name}), TYPE_OF_EDGE))

    list_node_name, list_score = [], []
    for (node_name, score) in gm.jaccard_similarity_top(root_node, label, top_k):
        list_node_name.append(node_name)
        list_score.append(score)

    return list_node_name, list_score

if __name__ == "__main__":
    
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "123123aA@"

    gm = GraphManager(uri, user, password)
    print(get_father_node_name(gm, Node(TYPE_OF_ENTITY_IN_KG, {"name": "Java"})))
    print(get_top_similar_node(gm, Node(TYPE_OF_CV, {"name": "Java Developer_26"}), [Node(TYPE_OF_ENTITY_IN_KG, {"name": "Java"})], TYPE_OF_JOB))
    # print(gm.jaccard_similarity_top(Node(TYPE_OF_CV, {"name": "Java Developer_25"}), TYPE_OF_JOB))