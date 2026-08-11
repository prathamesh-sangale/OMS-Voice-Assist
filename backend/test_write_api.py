import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/agent/command"

def test():
    print("Testing write operation...")
    
    # 1. Send update command
    payload = {"text": "update OR601 status to completed"}
    res = requests.post(API_URL, json=payload)
    data = res.json()
    
    print("1. Update Response:")
    print(json.dumps(data, indent=2))
    
    if data.get("status") == "confirmation_required":
        action_id = data["data"]["id"]
        print(f"\\nGot confirmation_id: {action_id}")
        
        # 2. Send confirm command
        confirm_payload = {"text": f"!confirm {action_id}"}
        res2 = requests.post(API_URL, json=confirm_payload)
        data2 = res2.json()
        print("\\n2. Confirm Response:")
        print(json.dumps(data2, indent=2))
    else:
        print("\\nDid not get confirmation_required status!")

if __name__ == "__main__":
    test()
