import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("IRIS System End-to-End Test")
print("=" * 60)

# Test 1: Health Check
print("\n[1] Testing Health Check...")
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"✅ Server is online: {r.json()}")
except Exception as e:
    print(f"❌ Server offline: {e}")
    exit(1)

# Test 2: Create New Session
print("\n[2] Creating New Session...")
try:
    r = requests.post(f"{BASE_URL}/sessions")
    session_data = r.json()
    session_id = session_data["session_id"]
    print(f"✅ Session created: {session_id}")
except Exception as e:
    print(f"❌ Failed to create session: {e}")
    exit(1)

# Test 3: Send First Query
print("\n[3] Sending Query 1: 'What are the total sales?'...")
try:
    r = requests.post(
        f"{BASE_URL}/query",
        json={"query": "What are the total sales?", "session_id": session_id}
    )
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Query 1 Success:")
        print(f"   SQL: {result.get('sql', 'N/A')[:80]}...")
        print(f"   Latency: {result.get('latency', 0):.2f}s")
    else:
        print(f"❌ Query 1 Failed: {r.status_code} - {r.text[:200]}")
except Exception as e:
    print(f"❌ Query 1 Error: {e}")

time.sleep(2)

# Test 4: Send Second Query (to test context)
print("\n[4] Sending Query 2: 'How many records?'...")
try:
    r = requests.post(
        f"{BASE_URL}/query",
        json={"query": "How many records?", "session_id": session_id}
    )
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Query 2 Success:")
        print(f"   SQL: {result.get('sql', 'N/A')[:80]}...")
    else:
        print(f"❌ Query 2 Failed: {r.status_code}")
except Exception as e:
    print(f"❌ Query 2 Error: {e}")

time.sleep(2)

# Test 5: Retrieve Session History
print("\n[5] Retrieving Session History...")
try:
    r = requests.get(f"{BASE_URL}/sessions/{session_id}")
    if r.status_code == 200:
        history = r.json()
        print(f"✅ History retrieved: {len(history)} messages")
        for i, msg in enumerate(history):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:60]
            print(f"   [{i+1}] {role}: {content}...")
    else:
        print(f"❌ History retrieval failed: {r.status_code}")
except Exception as e:
    print(f"❌ History Error: {e}")

# Test 6: List All Sessions
print("\n[6] Listing All Sessions...")
try:
    r = requests.get(f"{BASE_URL}/sessions")
    if r.status_code == 200:
        sessions = r.json()
        print(f"✅ Found {len(sessions)} session(s):")
        for s in sessions:
            print(f"   - {s.get('title', 'Untitled')}: {s.get('id', 'N/A')[:16]}...")
    else:
        print(f"❌ Session listing failed: {r.status_code}")
except Exception as e:
    print(f"❌ Listing Error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
