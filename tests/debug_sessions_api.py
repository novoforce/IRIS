import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_sessions():
    print(f"Testing GET /sessions at {BASE_URL}...")
    try:
        response = requests.get(f"{BASE_URL}/sessions")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error Detail: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_list_sessions()
