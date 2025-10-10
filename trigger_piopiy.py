# trigger_piopiy.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Your Render app URL (replace with your actual URL after deployment)
APP_URL = os.getenv("APP_URL", "https://call-ivr.onrender.com")

def make_call():
    payload = {
        "to": "+917756043094"  # Keep as string in your request, it will be converted to number in the API
    }
    
    try:
        response = requests.post(f"{APP_URL}/make-call", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json()
    except Exception as e:
        print(f"Error making call: {e}")
        return None

if __name__ == "__main__":
    result = make_call()
    if result:
        print("Call triggered successfully!")
    else:
        print("Failed to trigger call")