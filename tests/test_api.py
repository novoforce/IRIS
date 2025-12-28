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

    print("\nTesting /query endpoint (Amazon Sales)...")
    # Using a simple query that we know works
    payload = {"query": "How many records are there in amazon sales report?"}
    
    # Increase timeout if possible, or just expect it to take time
    # TestClient doesn't actually timeout usually since it calls directly python function
    response = client.post("/query", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Query Success!")
        print(f"Query: {data['query']}")
        print(f"SQL: {data['sql']}")
        print(f"Result: {data['result']}")
        if data['logs']:
             print("Logs present.")
    else:
        print(f"Query Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api()
