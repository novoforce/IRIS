from google import genai
from google.genai import types
import os
from typing import List
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from .base import EmbeddingService

class GeminiEmbedding(EmbeddingService, Embeddings):
    """
    Gemini implementation of EmbeddingService using google-genai (v2).
    """

    def __init__(self, api_key: str = None, model_name: str = "models/text-embedding-004"):
        """
        Initialize Gemini Embedding service.
        """
        load_dotenv('secrets/.env')
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or passed as argument.")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def generate_embedding(self, text: str) -> List[float]:
        """Generates embedding for a single text."""
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                title="Embedding of single text"
            )
        )
        return result.embeddings[0].values

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts using batch API."""
        if not texts:
            return []
            
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                result = self.client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        title="Batch embedding"
                    )
                )
                if result.embeddings:
                    # v2 returns list of ContentEmbedding objects, access .values
                    all_embeddings.extend([e.values for e in result.embeddings])
            except Exception as e:
                print(f"Error in batch embedding: {e}")
                raise e
                
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """LangChain compatibility alias for generate_embedding."""
        # For query, we might want a different task type, but using same for consistency for now
        # or use RETRIEVAL_QUERY if we were strict. 
        # But Qdrant logic typically matches document-document in this app context.
        return self.generate_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """LangChain compatibility alias for generate_embeddings."""
        return self.generate_embeddings(texts)
