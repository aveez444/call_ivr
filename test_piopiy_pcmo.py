# test_piopiy_pcmo.py
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

PIOPIY_SECRET = os.getenv("PIOPIY_SECRET")
PIOPIY_APP_ID = os.getenv("PIOPIY_APP_ID")

def test_pcmo_api():
    endpoint = "https://rest.telecmi.com/v2/ind_pcmo_make_call"
    
    # Convert appid to number
    appid_number = int(PIOPIY_APP_ID)
    
    # Different PCMO formats to try
    pcmo_formats = [
        # Format 1: Simple
        [{"action": "call", "answer_url": "https://call-ivr.onrender.com/call"}],
        
        # Format 2: With number
        [{"action": "call", "number": "virtual", "answer_url": "https://call-ivr.onrender.com/call"}],
        
        # Format 3: Detailed
        [{
            "action": "call", 
            "number": "dummy",
            "from": 917943446575,
            "answer_url": "https://call-ivr.onrender.com/call",
            "timeout": 30
        }]
    ]
    
    for i, pcmo in enumerate(pcmo_formats, 1):
        print(f"\n=== Testing PCMO Format {i} ===")
        print(f"PCMO: {json.dumps(pcmo, indent=2)}")
        
        # All numeric fields as numbers
        payload = {
            'appid': appid_number,  # Convert to number
            'secret': PIOPIY_SECRET,
            'from': 917943446575,   # As number
            'to': 917756043094,     # As number
            'pcmo': pcmo,
            'duration': 5400,       # As number
            'extra_params': {}
        }
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(endpoint, json=payload, timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print("✅ SUCCESS! Use this PCMO format.")
                    return pcmo, payload
        except Exception as e:
            print(f"Error: {e}")
    
    return None, None

if __name__ == "__main__":
    working_pcmo, working_payload = test_pcmo_api()
    if working_pcmo:
        print(f"\n🎉 Working PCMO format: {json.dumps(working_pcmo, indent=2)}")
        print(f"🎉 Working payload format: {json.dumps(working_payload, indent=2)}")
    else:
        print("\n❌ No PCMO format worked. Please check your credentials and documentation.")