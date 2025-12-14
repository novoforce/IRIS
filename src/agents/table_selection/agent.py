import sys
import os
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import BaseAgent
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.qdrant_store import QdrantStore
from qdrant_client import QdrantClient

class TableSelectionAgent(BaseAgent):
    def __init__(self, shared_client: QdrantClient = None):
        super().__init__(agent_name="table_selection")
        self.embedding_service = GeminiEmbedding()
        
        # Qdrant Setup
        collection_name = self.config.get('table_collection', 'table_descriptions')
        
        if shared_client:
            self.store = QdrantStore(collection_name=collection_name, client=shared_client)
        else:
            # Fallback to local path if no shared client (though Orchestrator should provide it)
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../qdrant_db'))
            self.store = QdrantStore(collection_name=collection_name, host=db_path)

    def execute(self, entities: List[str]) -> List[str]:
        """
        Selects relevant tables based on extracted entities.
        
        Args:
            entities (List[str]): List of entity terms to search for.
            
        Returns:
            List[str]: List of unique table names.
        """
        relevant_tables = set()
        top_k = self.config.get('top_k', 3)
        threshold = self.config.get('similarity_threshold', 0.65)
        
        print(f"TableSelection: Searching for {entities}")
        
        for entity in entities:
            query_vec = self.embedding_service.generate_embedding(entity)
            results = self.store.search_vectors(query_vec, limit=top_k)
            
            for res in results:
                if res['score'] >= threshold:
                    table_name = res['payload']['table_name']
                    relevant_tables.add(table_name)
                    print(f"  - Found table: {table_name} (Score: {res['score']:.4f})")
                    
        return list(relevant_tables)
