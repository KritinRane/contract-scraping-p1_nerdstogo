import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# 1. Upload API Key Credentials. 

load_dotenv()
SAM_API_Key = os.environ.get("SAM_API_KEY")



# 2. FIXED: Target the correct SAM.gov production path
url = "https://api.sam.gov/prod/opportunities/v2/search"

# 3. Calculate a dynamic date range (looking at bids posted in the last 90 days)
today = datetime.now()
ninety_days_ago = today - timedelta(days=90)

# FIXED: Removed the double 'd' typo so it outputs a clean MM/DD/YYYY format
posted_to = today.strftime("%m/%d/%Y")
posted_from = ninety_days_ago.strftime("%m/%d/%Y")

# 4. Define the query parameters according to the official GSA spec
params = {
    "api_key": SAM_API_KEY,
    "postedFrom": posted_from,
    "postedTo": posted_to,
    "state": "NJ",          # Restricts results specifically to New Jersey
    "limit": 10,            # Keeps the validation preview payload light
    "offset": 0
}

try:
    print(f"Querying SAM.gov for NJ opportunities posted between {posted_from} and {posted_to}...")
    
    # FIXED: Added a 10-second timeout parameter so the script fails gracefully instead of hanging
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    # Extract total record count
    total_records = data.get("totalRecords", 0)
    print(f"Successfully found {total_records} open federal opportunities in NJ.\n")
    
    # Pretty print the first few opportunities to inspect the schema
    opportunities = data.get("opportunitiesData", [])
    if opportunities:
        print(json.dumps(opportunities[:2], indent=2))
    else:
        print("No active opportunities found matching the criteria.")

except requests.exceptions.Timeout:
    print("\n[Error]: The connection timed out. The API gateway rejected the connection.")
except requests.exceptions.RequestException as e:
    print(f"\nAPI Connection Error: {e}")

if not SAM_API_KEY: 
    raise ValueError("environment variable is not set")

