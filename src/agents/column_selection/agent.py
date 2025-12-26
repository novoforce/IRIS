import sys
import os
import re
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# CustomBaseAgent for logic
from src.agents.base_agent import CustomBaseAgent
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.faiss_store import FaissStore

class ColumnSelectionAgent(CustomBaseAgent):
    def __init__(self):
        super().__init__(agent_name="column_selection")
        self.embedding_service = GeminiEmbedding()
        
    def _sanitize_collection_name(self, name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '_', name).lower()

    def execute(self, tables: List[str], attributes: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Selects relevant columns.
        """
        selected_columns = {}
        top_k = self.config.get('top_k', 5)
        distance_threshold = self.config.get('distance_threshold', 1.2) 
        
        print(f"ColumnSelection: Searching attributes {attributes} in tables {tables}")
        
        for table in tables:
            collection_name = f"columns_{self._sanitize_collection_name(table)}"
            
            try:
                store = FaissStore(index_name=collection_name, embedding_function=self.embedding_service, folder_path="faiss_db")
                table_columns = []
                
                for attr in attributes:
                    results = store.search_similarity(attr, k=top_k)
                    
                    for res in results:
                        if res['score'] <= distance_threshold:
                            col_info = {
                                "name": res['payload']['column_name'],
                                "description": res['content'],
                                "score": res['score']
                            }
                            # Check duplicates by name
                            if not any(c['name'] == col_info['name'] for c in table_columns):
                                table_columns.append(col_info)
                                print(f"    - Found column: {col_info['name']} (Distance: {res['score']:.4f})")
                
                if table_columns:
                    selected_columns[table] = table_columns
                    
            except Exception as e:
                # Index might not exist
                print(f"    Warning: Could not search columns for table '{table}': {e}")
                
        return selected_columns
