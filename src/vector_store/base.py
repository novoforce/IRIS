from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class VectorStore(ABC):
    """
    Abstract Base Class for Vector Store operations.
    """

    @abstractmethod
    def connect(self):
        """Establishes connection to the vector database."""
        pass

    @abstractmethod
    def upsert_vectors(self, vectors: List[List[float]], metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """
        Upserts vectors into the database.
        
        Args:
            vectors (List[List[float]]): List of embedding vectors.
            metadata (List[Dict[str, Any]]): List of metadata dictionaries corresponding to vectors.
            ids (List[str], optional): List of unique IDs. If None, IDs should be generated.
        """
        pass

    @abstractmethod
    def search_vectors(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches for similar vectors.
        
        Args:
            query_vector (List[float]): The query embedding vector.
            limit (int): Number of results to return.
            
        Returns:
            List[Dict[str, Any]]: List of results with metadata and scores.
        """
        pass
