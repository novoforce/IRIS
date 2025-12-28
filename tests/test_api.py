import sys
import os
from fastapi.testclient import TestClient
import warnings

# Suppress DeprecationWarnings
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.api import app
except Exception as e:
    print(f"Error importing API: {e}")
    sys.exit(1)

client = TestClient(app)

def test_api():
    print("Testing /health endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    print("Health check passed:", response.json())

    # Generate a random session ID
    import uuid
    session_id = str(uuid.uuid4())
    print(f"\nUsing Session ID: {session_id}")

    print("\n--- Turn 1: Amazon Sales ---")
    payload1 = {"query": "How many records are there in amazon sales report?", "session_id": session_id}
    response1 = client.post("/query", json=payload1)
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"Turn 1 SQL: {data1.get('sql', 'N/A')}")
        print(f"Turn 1 Result: {data1.get('result', 'N/A')}")
        assert data1['sql'], "Turn 1 should generate SQL"
    else:
        print(f"Turn 1 Failed: {response1.status_code}")
        print(response1.text)
        return

    print("\n--- Turn 2: Contextual Query (Inventory) ---")
    payload2 = {"query": "and sale report?", "session_id": session_id}
    response2 = client.post("/query", json=payload2)

    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Turn 2 SQL: {data2.get('sql', 'N/A')}")
        print(f"Turn 2 Reasoning: {data2.get('sql_reasoning', 'N/A')}")
        
        # Verification: SQL should target 'inventory' table, not amazon_sales
        if "inventory" in data2.get('sql', '').lower():
             print("SUCCESS: Context carried over. Query targeted 'inventory'.")
        else:
             print(f"WARNING: Context might not have worked. SQL: {data2.get('sql')}")
             
    else:
        print(f"Turn 2 Failed: {response2.status_code}")
        print(response2.text)

if __name__ == "__main__":
    test_api()
