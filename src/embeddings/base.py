from abc import ABC, abstractmethod
from typing import List

class EmbeddingService(ABC):
    """
    Abstract Base Class for Embedding Services.
    """

    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for a single text string.
        
        Args:
            text (str): Input text.
            
        Returns:
            List[float]: Embedding vector.
        """
        pass
    
    @abstractmethod
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of input texts.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        pass
