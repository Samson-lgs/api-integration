"""
Test CPCB API to see the actual data structure
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('CPCB_API_KEY')
base_url = "https://api.data.gov.in/resource"
endpoint = f"{base_url}/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"

params = {
    'api-key': api_key,
    'format': 'json',
    'limit': 5  # Get just 5 records to see structure
}

print("Fetching sample data from CPCB API...")
response = requests.get(endpoint, params=params, timeout=30)

if response.status_code == 200:
    data = response.json()
    print("\nAPI Response Structure:")
    print("="*70)
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
