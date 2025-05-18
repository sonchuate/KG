import chromadb
from chromadb.config import Settings
import numpy as np
class ChromaDBManager:
    def __init__(self, collection_name="my_collection", host="localhost", port=8000):
        self.client = chromadb.HttpClient(host='localhost', port=port)
        try:
            self.client.delete_collection("my_collection")
        except:
            print('Not exist')
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, ids: list, documents: list, embeddings: list = None, metadatas: list = None):
        """
        Thêm tài liệu vào collection.
        - ids: danh sách ID duy nhất.
        - documents: danh sách nội dung văn bản.
        - embeddings: danh sách vector tương ứng (tùy chọn).
        - metadatas: danh sách metadata (tùy chọn).
        """
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_texts: list= None, n_results: int = 3, query_embeddings: list = None):
        """
        Truy vấn tương tự với văn bản hoặc embedding.
        - query_texts: văn bản cần tìm tương tự (nếu không dùng embedding).
        - query_embeddings: nếu có vector embedding sẵn.
        """
        return self.collection.query(
            query_texts=query_texts if query_embeddings is None else None,
            query_embeddings=query_embeddings,
            n_results=n_results
        )

    def delete_by_ids(self, ids: list):
        """Xoá tài liệu theo ID."""
        self.collection.delete(ids=ids)

    def reset_collection(self):
        """Xoá toàn bộ dữ liệu trong collection."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)

    def list_collections(self):
        return self.client.list_collections()


if __name__ == "__main__":
    db = ChromaDBManager()
    ## mặc định embedding ra 384 chiều
    db.add_documents(
        ids=["doc1", "doc2"],
        documents=["The quick brown fox", "A legal document about traffic laws"],
        metadatas=[{"type": "text"}, {"type": "legal"}],
        # embeddings = np.array([[1, 0], [0, 1]])
    )

    # result = db.query(["The quick"], query_embeddings=np.array([0, 1]))
    # print("Kết quả truy vấn:", result)

    result = db.query(["The quick"])
    print("Kết quả truy vấn:", result)

    db.delete_by_ids(["doc1"])
