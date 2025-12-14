import sys
import os
import traceback

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.qdrant_store import QdrantStore
from qdrant_client import QdrantClient

def test_search():
    print("--- Testing Vector Search ---")
    
    try:
        embedding_service = GeminiEmbedding()
        
        # Shared Client setup
        # Note: We need to point to the correct DB path relative to execution or absolute
        # Given we run from root, 'qdrant_db' is in root.
        db_path = os.path.abspath("qdrant_db")
        shared_client = QdrantClient(path=db_path)
        
        # 1. Search Columns in Amazon Sale Report
        print("\nSearching for 'shipped' in Amazon Sale Report columns...")
        query_vec = embedding_service.generate_embedding("shipped")
        
        column_store_amazon = QdrantStore(collection_name='columns_amazon_sale_report', client=shared_client)
        results = column_store_amazon.search_vectors(query_vec, limit=2)
        for res in results:
            payload = res['payload']
            print(f"- {payload['column_name']} (Score: {res['score']:.4f})")

        # 2. Search Columns in International Sale Report
        print("\nSearching for 'gross amount' in International Sale Report columns...")
        query_vec_intl = embedding_service.generate_embedding("gross amount")
        
        column_store_intl = QdrantStore(collection_name='columns_international_sale_report', client=shared_client)
        results = column_store_intl.search_vectors(query_vec_intl, limit=2)
        for res in results:
            payload = res['payload']
            print(f"- {payload['column_name']} (Score: {res['score']:.4f})")

        # 3. Search Tables
        print("\nSearching for 'inventory' in tables...")
        query_vec_table = embedding_service.generate_embedding("inventory")
        
        table_store = QdrantStore(collection_name='table_descriptions', client=shared_client)
        results = table_store.search_vectors(query_vec_table, limit=2)
        for res in results:
            payload = res['payload']
            print(f"- {payload['table_name']} (Score: {res['score']:.4f})")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
