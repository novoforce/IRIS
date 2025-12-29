import requests
import uuid
import time
import sys

BASE_URL = "http://localhost:8000"

def run_api_tests():
    print(f"--- Starting API Verification at {BASE_URL} ---")
    
    # 1. Health Check
    print("\n[1] Health Check...")
    try:
        res = requests.get(f"{BASE_URL}/")
        res.raise_for_status()
        print(f"✅ Status: {res.json()['status']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # 2. Create Session
    print("\n[2] Creating Session...")
    res = requests.post(f"{BASE_URL}/sessions")
    session_id = res.json()["session_id"]
    print(f"✅ Session ID: {session_id}")

    # 3. List Sessions
    print("\n[3] Listing Sessions...")
    res = requests.get(f"{BASE_URL}/sessions")
    sessions = res.json()
    if any(s['id'] == session_id for s in sessions):
        print(f"✅ Created session found in list (Total: {len(sessions)})")
    else:
        print(f"❌ Created session NOT in list!")
        return False

    # 4. Multi-turn Query Test
    print("\n[4] Query Turn 1: 'What tables are available?'")
    res1 = requests.post(f"{BASE_URL}/query", json={"query": "What tables are available?", "session_id": session_id})
    if res1.status_code == 200:
        print("✅ Query 1 Success.")
    else:
        print(f"❌ Query 1 Failed: {res1.text}")
        return False

    print("\n[5] Query Turn 2: 'how many records in amazon sales?'")
    res2 = requests.post(f"{BASE_URL}/query", json={"query": "how many records in amazon sales?", "session_id": session_id})
    if res2.status_code == 200:
        print(f"✅ Query 2 Success. Result: {res2.json()['result']}")
    else:
        print(f"❌ Query 2 Failed: {res2.text}")
        return False

    # 5. Verify Persistence & History
    print("\n[6] Verifying History Retrieval...")
    time.sleep(1) # Wait for potential async persist
    res_hist = requests.get(f"{BASE_URL}/sessions/{session_id}")
    history = res_hist.json()
    if len(history) >= 4: # 2 turns = 4 messages (User+Bot x 2)
        print(f"✅ History retrieved. Message count: {len(history)}")
        for msg in history:
            print(f"   - {msg['role']}: {msg['content'][:50]}...")
    else:
        print(f"❌ History incomplete: {len(history)} messages found.")
        return False

    print("\n--- API Verification Passed! ---")
    return True

if __name__ == "__main__":
    if run_api_tests():
        sys.exit(0)
    else:
        sys.exit(1)
