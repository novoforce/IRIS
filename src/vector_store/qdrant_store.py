from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import uuid
from .base import VectorStore

class QdrantStore(VectorStore):
    """
    Qdrant implementation of VectorStore.
    """

    def __init__(self, collection_name: str, host: str = ":memory:", client: Optional[QdrantClient] = None):
        """
        Initialize Qdrant client.
        
        Args:
            collection_name (str): Name of the collection.
            host (str): Qdrant host. Defaults to ":memory:" for local in-memory instance.
                        Use "path/to/db" for local persistence.
            client (QdrantClient, optional): Existing QdrantClient instance.
        """
        self.collection_name = collection_name
        self.host = host
        self.client = client

    def connect(self):
        """Establishes connection to Qdrant."""
        if self.client is None:
            if self.host == ":memory:":
                self.client = QdrantClient(location=":memory:")
            elif self.host.startswith("http"):
                self.client = QdrantClient(url=self.host)
            else:
                # Assume local path
                self.client = QdrantClient(path=self.host)
            
    def _ensure_collection(self, vector_size: int):
        """Ensures the collection exists."""
        if self.client is None:
            self.connect()
            
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )

    def upsert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """Upserts vectors into Qdrant."""
        if not vectors:
            return
            
        vector_size = len(vectors[0])
        self._ensure_collection(vector_size)
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
            
        points = [
            models.PointStruct(id=id_, vector=vector, payload=meta)
            for id_, vector, meta in zip(ids, vectors, metadata)
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search_vectors(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Searches for similar vectors in Qdrant."""
        if self.client is None:
            self.connect()
            
        # Use query_points as search is missing
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ).points
        
        return [
            {"id": hit.id, "score": hit.score, "payload": hit.payload}
            for hit in results
        ]
