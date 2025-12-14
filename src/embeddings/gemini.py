import google.generativeai as genai
import os
from typing import List
from dotenv import load_dotenv
from .base import EmbeddingService

class GeminiEmbedding(EmbeddingService):
    """
    Gemini implementation of EmbeddingService.
    """

    def __init__(self, api_key: str = None, model_name: str = "models/embedding-001"):
        """
        Initialize Gemini Embedding service.
        
        Args:
            api_key (str, optional): API Key. If None, loads from environment.
            model_name (str): Name of the embedding model.
        """
        load_dotenv('secrets/.env')
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or passed as argument.")
            
        genai.configure(api_key=self.api_key)
        self.model_name = model_name

    def generate_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text."""
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document",
            title="Embedding of single text"
        )
        return result['embedding']

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts using batch API."""
        if not texts:
            return []
            
        # The genai.embed_content method supports a list of content
        # However, there might be limits on batch size (e.g., 100).
        # We'll implement a simple chunking mechanism just in case.
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                result = genai.embed_content(
                    model=self.model_name,
                    content=batch,
                    task_type="retrieval_document",
                    title="Batch embedding"
                )
                # result['embedding'] will be a list of embeddings for the batch
                if 'embedding' in result:
                    all_embeddings.extend(result['embedding'])
            except Exception as e:
                print(f"Error in batch embedding: {e}")
                # Fallback to single if batch fails? Or just raise.
                # For now, let's try to continue or re-raise.
                raise e
                
        return all_embeddings
