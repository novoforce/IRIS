import sys
import os
from typing import List

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Use CustomBaseAgent for non-LLM logic agents
from src.agents.base_agent import CustomBaseAgent
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.faiss_store import FaissStore

class TableSelectionAgent(CustomBaseAgent):
    def __init__(self):
        super().__init__(agent_name="table_selection")
        self.embedding_service = GeminiEmbedding()
        
        # FAISS Setup
        collection_name = self.config.get('table_collection', 'table_descriptions')
        self.store = FaissStore(index_name=collection_name, embedding_function=self.embedding_service, folder_path="faiss_db")

    def execute(self, entities: List[str]) -> List[str]:
        """
        Selects relevant tables based on extracted entities.
        """
        relevant_tables = set()
        top_k = self.config.get('top_k', 3)
        # FAISS L2: Lower is better. 0 = identical.
        # We'll use a distance threshold. Large distance = bad match.
        distance_threshold = self.config.get('distance_threshold', 1.0) 
        
        print(f"TableSelection: Searching for {entities}")
        
        for entity in entities:
            # FAISS Store handles embedding internally via LangChain wrapper
            results = self.store.search_similarity(entity, k=top_k)
            
            for res in results:
                # res has 'score' which is L2 distance
                if res['score'] <= distance_threshold:
                    table_name = res['payload']['table_name']
                    relevant_tables.add(table_name)
                    print(f"  - Found table: {table_name} (Distance: {res['score']:.4f})")
                    
        return list(relevant_tables)
