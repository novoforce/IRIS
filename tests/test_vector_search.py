import sys
import os
import traceback

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.embeddings.gemini import GeminiEmbedding
from src.vector_store.faiss_store import FaissStore

def test_search():
    print("--- Testing Vector Search (FAISS) ---")
    
    try:
        embedding_service = GeminiEmbedding()
        
        # 1. Search Columns in Amazon Sale Report
        print("\nSearching for 'shipped' in Amazon Sale Report columns...")
        
        # Note: Index names must match ingest_vectors.py
        column_store_amazon = FaissStore(index_name='columns_amazon_sale_report', embedding_function=embedding_service, folder_path="faiss_db")
        results = column_store_amazon.search_similarity("shipped", k=2)
        
        for res in results:
            payload = res['payload']
            print(f"- {payload['column_name']} (Distance: {res['score']:.4f})")

        # 2. Search Columns in International Sale Report
        print("\nSearching for 'gross amount' in International Sale Report columns...")
        
        column_store_intl = FaissStore(index_name='columns_international_sale_report', embedding_function=embedding_service, folder_path="faiss_db")
        results = column_store_intl.search_similarity("gross amount", k=2)
        
        for res in results:
            payload = res['payload']
            print(f"- {payload['column_name']} (Distance: {res['score']:.4f})")

        # 3. Search Tables
        print("\nSearching for 'inventory' in tables...")
        
        table_store = FaissStore(index_name='table_descriptions', embedding_function=embedding_service, folder_path="faiss_db")
        results = table_store.search_similarity("inventory", k=2)
        
        for res in results:
            payload = res['payload']
            print(f"- {payload['table_name']} (Distance: {res['score']:.4f})")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_search()
