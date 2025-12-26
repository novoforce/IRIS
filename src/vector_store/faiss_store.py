import os
import faiss
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document

class FaissStore:
    def __init__(self, index_name: str, embedding_function: Any, dim: int = 768, folder_path: str = "faiss_indices"):
        """
        Wrapper for LangChain FAISS store.
        :param index_name: Name of the index (used for saving/loading).
        :param embedding_function: LangChain compatible embedding function OR a custom wrapper that has `embed_query`.
        :param dim: Dimension of embeddings (default 768 for Gemini).
        :param folder_path: Folder to store FAISS indices.
        """
        self.index_name = index_name
        self.embedding_function = embedding_function
        self.dim = dim
        self.folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', folder_path))
        
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        self.vector_store = self._load_or_create()

    def _load_or_create(self) -> FAISS:
        try:
            # Try loading existing index
            return FAISS.load_local(
                folder_path=self.folder_path,
                index_name=self.index_name,
                embeddings=self.embedding_function,
                allow_dangerous_deserialization=True
            )
        except RuntimeError:
            # If not found, create new
            print(f"Creating new FAISS index: {self.index_name}")
            index = faiss.IndexFlatL2(self.dim)
            return FAISS(
                embedding_function=self.embedding_function,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={},
            )

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the store.
        :param documents: List of dicts with 'content' and 'metadata'.
        """
        docs = [
            Document(page_content=d['content'], metadata=d.get('metadata', {})) 
            for d in documents
        ]
        self.vector_store.add_documents(docs)
        self.save_local()

    def search_similarity(self, query: str, k: int = 3, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        Returns list of results with score.
        """
        # score_threshold filters results with score < threshold (for cosine sim) or distance > threshold (L2).
        # FAISS uses L2 distance by default (lower is better) or Inner Product (higher is better).
        # Wrapper uses whatever index is provided. IndexFlatL2 is L2 distance.
        # LangChain's similarity_search_with_score returns L2 distance for L2 index.
        # So "threshold" interpretation depends on metric. 
        # For simplicity, we return everything top_k and let agent filter.
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        formatted_results = []
        for doc, score in results:
            # Convert L2 distance to a similarity score if needed, or just pass raw.
            # L2 is 0-inf (lower is better).
            # We might want to normalize or just return score.
            # Let's return raw score and payload equivalent.
            formatted_results.append({
                'payload': doc.metadata,  # Map metadata to payload for compatibility
                'content': doc.page_content,
                'score': float(score) # L2 distance
            })
            
        return formatted_results

    def save_local(self):
        self.vector_store.save_local(folder_path=self.folder_path, index_name=self.index_name)
