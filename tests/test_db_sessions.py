import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:8001"

def test_db_sessions():
    print(f"Testing API at {BASE_URL}...")
    
    # 1. Create a New Session
    print("\n[1] Creating New Session...")
    try:
        res = requests.post(f"{BASE_URL}/sessions")
        res.raise_for_status()
        session_id = res.json()["session_id"]
        print(f"✅ Created Session: {session_id}")
    except Exception as e:
        print(f"❌ Failed to create session: {e}")
        sys.exit(1)

    # 2. List Sessions (Verify it appears)
    print("\n[2] Listing Sessions...")
    res = requests.get(f"{BASE_URL}/sessions")
    sessions = res.json()
    found = any(s['id'] == session_id for s in sessions)
    if found:
        print(f"✅ Session {session_id} found in list. Total sessions: {len(sessions)}")
    else:
        print(f"❌ Session {session_id} NOT found in list: {sessions}")

    # 3. Chat (Turn 1) - Should persist
    print("\n[3] Sending Query (Turn 1)...")
    query1 = "What tables are available?"
    res = requests.post(f"{BASE_URL}/query", json={"query": query1, "session_id": session_id})
    if res.ok:
        print("✅ Query 1 successful.")
    else:
        print(f"❌ Query 1 failed: {res.text}")

    # 4. Verify History
    print("\n[4] verifying History...")
    # Give a brief moment for async save if needed (though it should be awaited)
    time.sleep(1) 
    res = requests.get(f"{BASE_URL}/sessions/{session_id}")
    history = res.json()
    
    # Expecting: User query + Bot response
    if len(history) >= 2:
        print(f"✅ History retrieved. Count: {len(history)}")
        print(f"   Last User Message: {history[-2]['content']}")
        print(f"   Last Bot Message: {history[-1]['content']}")
    else:
        print(f"❌ History incomplete or missing. Count: {len(history)}")
        print(history)

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    test_db_sessions()
