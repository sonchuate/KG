from neo4j import GraphDatabase
from src.preprocess.utils import process_string

class Node:
    def __init__(self, label: str, properties: dict):
        self.label = label
        self.properties = properties

    def create(self, driver):
        """Thêm node vào Neo4j"""
        # Duyệt các key trong properties để build câu MERGE
        if "name" not in self.properties:
            raise ValueError("Node must have a 'name' property to merge.")

        query = f"""
        MERGE (n:{self.label} {{name: $name}})
        """

        with driver.session() as session:
            try:
                session.run(query, name=process_string(self.properties["name"]))
            except Exception as e:
                print("Neo4j Error:", e)

    def delete(self, driver):
        """Xoá node khỏi Neo4j"""
        query = f"MATCH (n:{self.label} {{name: $name}}) DETACH DELETE n"
        with driver.session() as session:
            session.run(query, name=process_string(self.properties.get("name")))

class Edge:
    def __init__(self, src_node: Node, trg_node: Node, rel_type: str):
        self.src_node = src_node
        self.trg_node = trg_node
        self.rel_type = rel_type

    def create(self, driver):
        """Thêm cạnh giữa 2 node vào Neo4j"""
        query = f"""
        MERGE  (a:{self.src_node.label} {{name: $from_name}})
        MERGE  (b:{self.trg_node.label} {{name: $to_name}})
        MERGE  (a)-[r:{self.rel_type} ]->(b)
        """
        with driver.session() as session:
            session.run(
                query, from_name=process_string(self.src_node.properties.get("name")),
                to_name=process_string(self.trg_node.properties.get("name")),
            )

    def delete(self, driver):
        """Xoá cạnh giữa 2 node"""
        query = f"""
        MATCH (a:{self.src_node.label} {{name: $from_name}})-[r:{self.rel_type}]->(b:{self.trg_node.label} {{name: $to_name}})
        DELETE r
        """
        with driver.session() as session:
            session.run(query, from_name=process_string(self.src_node.properties.get("name")),
                        to_name=process_string(self.trg_node.properties.get("name"))
            )
    
class Graph:
    def __init__(self, list_nodes:list[Node], list_edges:list[Edge]):
        self.list_nodes = list_nodes
        self.list_edges = list_edges

    def create(self, driver):
        """Thêm cạnh giữa 2 node vào Neo4j"""
        for node in self.list_nodes:
            node.create(driver)
        
        for edge in self.list_edges:
            edge.create(driver)
    
    def delete(self, driver):
        for node in self.list_nodes:
            node.delete(driver)
        
        for edge in self.list_edges:
            edge.delete(driver)

class NodeRelation:
    def __init__(self, node:Node, relationship:str):
        self.node = node
        self.relationship = relationship

class GraphManager:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_node(self, node: Node):
        """Thêm node vào Neo4j"""
        node.create(self.driver)

    def add_edge(self, edge: Edge):
        """Thêm cạnh vào Neo4j"""
        edge.create(self.driver)

    def add_graph(self, nodes: list, edges: list):
        """Thêm toàn bộ đồ thị vào Neo4j"""
        with self.driver.session() as session:
            for node in nodes:
                node.create(self.driver)

            for edge in edges:
                edge.create(self.driver)

    def delete_node(self, node: Node):
        """Xoá node khỏi Neo4j"""
        node.delete(self.driver)

    def delete_edge(self, edge: Edge):
        """Xoá cạnh khỏi Neo4j"""
        edge.delete(self.driver)

    def clear_graph(self):
        """Xoá toàn bộ đồ thị"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")


    def get_related_nodes(self, node: Node) -> list[NodeRelation]:
        """
        Lấy ra các đỉnh và quan hệ có liên kết với node A.
        Trả về danh sách gồm các dict: {"node": Node, "relationship": str}
        """
        query = f"""
        MATCH (a:{node.label} {{name: $name}})-[r]-(b)
        RETURN labels(b)[0] AS label, b AS node, type(r) AS relationship
        """
        related_nodes = []
        with self.driver.session() as session:
            result = session.run(query, name=process_string(node.properties["name"]))
            for record in result:
                related_node = Node(label=record["label"], properties=dict(record["node"]))
                related_nodes.append(
                    NodeRelation(related_node, record["relationship"])
                )

        return related_nodes

    def get_relations_to_node(self, node: Node) -> list[NodeRelation]:
        """
        Lấy các quan hệ **tới** node đầu vào.
        Trả về danh sách gồm các dict: {"node": Node, "relationship": str}
        """
        query = f"""
        MATCH (a)-[r]->(b:{node.label} {{name: $name}})
        RETURN labels(a)[0] AS label, a AS node, type(r) AS relationship
        """
        relations_to_node = []
        with self.driver.session() as session:
            result = session.run(query, name=process_string(node.properties["name"]))
            for record in result:
                from_node = Node(label=record["label"], properties=dict(record["node"]))
                relations_to_node.append(
                    NodeRelation(from_node, record["relationship"])
                )

        return relations_to_node

    def get_relations_from_node(self, node: Node) -> list[NodeRelation]:
        """
        Lấy các quan hệ **từ** node đầu vào.
        Trả về danh sách gồm các dict: {"node": Node, "relationship": str}
        """
        query = f"""
        MATCH (a:{node.label} {{name: $name}})-[r]->(b)
        RETURN labels(b)[0] AS label, b AS node, type(r) AS relationship
        """
        relations_from_node = []
        with self.driver.session() as session:
            result = session.run(query, name=process_string(node.properties["name"]))
            for record in result:
                to_node = Node(label=record["label"], properties=dict(record["node"]))
                relations_from_node.append(
                    NodeRelation(to_node, record["relationship"])
                )

        return relations_from_node
    
    def shortest_distance(self, name1: str, name2: str, max_length=10) -> int:
        name1 = process_string(name1)
        name2 = process_string(name2)
        if name1 == name2:
            return 0
        
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (a {{name: $name1}}), (b {{name: $name2}}),
                    p = shortestPath((a)-[*..{max_length}]-(b))
                RETURN length(p) AS distance
                """,
                name1=name1, name2=name2
            )
            record = result.single()
            return record["distance"] if record else -1
    
    def delete_data(self):
        """
        Xóa toàn bộ dữ liệu trong cơ sở dữ liệu Neo4j.
        """
        driver = self.driver
        try:
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            print("Đã xóa thành công toàn bộ dữ liệu trong Neo4j.")
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
        finally:
            driver.close()
            
def main():
    # Khởi tạo kết nối Neo4j
    g = GraphManager("neo4j://localhost:7687", "neo4j", "123123aA@")

    # Tạo node A và các node khác
    node1 = Node("Person", {"name": "Alice"})
    node2 = Node("Person", {"name": "Bob"})
    node3 = Node("City", {"name": "Hanoi"})
    node4 = Node("City", {"name": "Ho Chi Minh"})

    # Thêm các node vào Neo4j
    g.add_node(node1)
    g.add_node(node2)
    g.add_node(node3)
    g.add_node(node4)

    # Tạo các cạnh (edge)
    edge1 = Edge(node1, node2, "KNOWS")
    edge4 = Edge(node3, node1, "LIVES_IN")  # Mối quan hệ ngược

    # Thêm các cạnh vào Neo4j
    g.add_edge(edge1)
    g.add_edge(edge4)

    # Lấy ra các node có liên quan đến "Alice"
    related_nodes = g.get_relations_to_node(Node("Person", {"name": "Alice"}))
    
    print("Nodes related to Alice:")
    for related_node in related_nodes:
        print(f"Node:  {related_node.node.label} {related_node.node.properties}, Relationship: {related_node.relationship}")
    g.clear_graph()
    g.close()

if __name__ == "__main__":
    main()