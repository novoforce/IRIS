import subprocess
import time
import requests
import sys
import os

def run_all_in_one():
    print("--- Starting Full System Integration Test ---")
    
    # 1. Start Server
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api:app", "--port", "8003"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=os.getcwd()
    )
    
    # Wait for server to warm up
    time.sleep(10)
    
    # Check if server is still alive
    if server_process.poll() is not None:
        stdout, stderr = server_process.communicate()
        print("❌ Server failed to start!")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    print("✅ Server process started. Running API tests...")
    
    success = True
    try:
        # Run test sequence
        BASE_URL = "http://localhost:8003"
        
        # Health Check
        print("\n[1] Health Check...")
        res = requests.get(f"{BASE_URL}/")
        print(f"✅ Healthy: {res.json()['status']}")
        
        # Create Session
        print("\n[2] Creating Session...")
        res = requests.post(f"{BASE_URL}/sessions")
        session_id = res.json()["session_id"]
        print(f"✅ Session: {session_id}")
        
        # Query
        print("\n[3] Query: 'Who are my top customers?'")
        res = requests.post(f"{BASE_URL}/query", json={"query": "Who are my top customers?", "session_id": session_id})
        if res.status_code == 200:
            print(f"✅ Query Success: {res.json()['sql']}")
        else:
            print(f"❌ Query Failed: {res.text}")
            success = False
            
        # History
        print("\n[4] History Verification...")
        res = requests.get(f"{BASE_URL}/sessions/{session_id}")
        history = res.json()
        if len(history) >= 2:
            print(f"✅ History retrieved ({len(history)} messages)")
        else:
            print(f"❌ History empty or incomplete: {history}")
            success = False
            
    except Exception as e:
        print(f"❌ Test encountered error: {e}")
        success = False
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except:
            server_process.kill()
            
    return success


# Redirect stdout/stderr to file
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("D:\\IRIS\\tests\\final_test_log.txt", "w", encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()
sys.stderr = sys.stdout

if __name__ == "__main__":
    if run_all_in_one():
        print("\n--- ALL TESTS PASSED! ---")
        sys.exit(0)
    else:
        print("\n--- TESTS FAILED! ---")
        sys.exit(1)
