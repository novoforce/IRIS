import sys
import os
import shutil
import uuid

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vector_store.qdrant_store import QdrantStore

def test_qdrant_store():
    print("--- Testing QdrantStore Isolation ---")
    
    # Use a temporary local path for testing
    test_db_path = "test_qdrant_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
        
    try:
        # 1. Initialize
        print("Initializing QdrantStore...")
        store = QdrantStore(collection_name="test_collection", host=test_db_path)
        store.connect()
        print("Connected.")
        with open("client_methods.txt", "w") as f:
            f.write("\n".join(dir(store.client)))
        print("Methods written to client_methods.txt")
        
        # 2. Upsert
        print("Upserting vectors...")
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [{"name": "vec1"}, {"name": "vec2"}]
        ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        
        store.upsert_vectors(vectors, metadata, ids)
        print("Upsert successful.")
        
        # 3. Search
        print("Searching vectors...")
        query = [0.1, 0.2, 0.3]
        results = store.search_vectors(query, limit=1)
        
        print(f"Search results: {results}")
        
        if len(results) > 0:
            print("Test PASSED: Found results.")
        else:
            print("Test FAILED: No results found.")
            
    except Exception as e:
        print(f"Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(test_db_path):
            try:
                shutil.rmtree(test_db_path)
            except:
                pass

if __name__ == "__main__":
    test_qdrant_store()
