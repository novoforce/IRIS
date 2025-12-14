import sys
import os
import re
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agents.base_agent import BaseAgent
from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.qdrant_store import QdrantStore
from qdrant_client import QdrantClient

class ColumnSelectionAgent(BaseAgent):
    def __init__(self, shared_client: QdrantClient = None):
        super().__init__(agent_name="column_selection")
        self.embedding_service = GeminiEmbedding()
        self.shared_client = shared_client
        
        # Fallback local path
        if not self.shared_client:
             db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../qdrant_db'))
             self.shared_client = QdrantClient(path=db_path)

    def _sanitize_collection_name(self, name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]', '_', name).lower()

    def execute(self, tables: List[str], attributes: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Selects relevant columns for the chosen tables based on attributes.
        
        Args:
            tables (List[str]): List of selected table names.
            attributes (List[str]): List of attribute terms to search for.
            
        Returns:
            Dict[str, List[Dict]]: Dictionary mapping table names to list of column info (name, score, desc).
        """
        selected_columns = {}
        top_k = self.config.get('top_k', 5)
        threshold = self.config.get('similarity_threshold', 0.60)
        
        print(f"ColumnSelection: Searching attributes {attributes} in tables {tables}")
        
        for table in tables:
            collection_name = f"columns_{self._sanitize_collection_name(table)}"
            print(f"  - Searching in collection: {collection_name}")
            
            try:
                store = QdrantStore(collection_name=collection_name, client=self.shared_client)
                table_columns = []
                
                for attr in attributes:
                    query_vec = self.embedding_service.generate_embedding(attr)
                    results = store.search_vectors(query_vec, limit=top_k)
                    
                    for res in results:
                        if res['score'] >= threshold:
                            col_info = {
                                "name": res['payload']['column_name'],
                                "description": res['payload']['content'],
                                "score": res['score']
                            }
                            # Avoid duplicates
                            if col_info not in table_columns:
                                table_columns.append(col_info)
                                print(f"    - Found column: {col_info['name']} (Score: {res['score']:.4f})")
                
                if table_columns:
                    selected_columns[table] = table_columns
                    
            except Exception as e:
                print(f"    - Error searching collection {collection_name}: {e}")
                
        return selected_columns
