import requests
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SAM_API_KEY = os.environ.get("SAM_API_KEY")
if not SAM_API_KEY:
    raise ValueError("SAM_API_KEY environment variable is not set")

URL = "https://api.sam.gov/opportunities/v2/search"

today = datetime.now()
posted_to = today.strftime("%m/%d/%Y")
posted_from = (today - timedelta(days=90)).strftime("%m/%d/%Y")

IT_KEYWORDS = [
    "information technology", "software", "cybersecurity",
    "network", "it support", "cloud", "data", "cyber",
    "helpdesk", "infrastructure", "systems integration",
    "modernization", "technical services", "telecommunications"
]

IT_NAICS = {
    "511210", "517110", "517210", "517910", "518210",
    "519130", "541511", "541512", "541513", "541519",
    "541690", "541715", "611420",
}

def is_it_related(opp):
    title = opp.get("title", "").lower()
    naics = opp.get("naicsCode", "")
    return any(kw in title for kw in IT_KEYWORDS) or naics in IT_NAICS

def is_still_open(opp):
    deadline = opp.get("responseDeadLine")
    if not deadline:
        return True
    try:
        dl = datetime.fromisoformat(deadline)
        now = datetime.now(timezone.utc)
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        return dl > now
    except:
        return True

params = {
    "api_key": SAM_API_KEY,
    "postedFrom": posted_from,
    "postedTo": posted_to,
    "ptype": "o,k,r,p,s",
    "limit": 1000,
    "offset": 0
}

print(f"Querying SAM.gov for IT opportunities between {posted_from} and {posted_to}...\n")

try:
    response = requests.get(URL, params=params, timeout=(5, 30))
    response.raise_for_status()
    data = response.json()

    opportunities = data.get("opportunitiesData", [])
    it_opps = [opp for opp in opportunities if is_it_related(opp) and is_still_open(opp)]

    print(f"Total results: {data.get('totalRecords', 0)}")
    print(f"IT-related and still open: {len(it_opps)}\n")

    for opp in it_opps:
        print(f"Title:    {opp.get('title')}")
        print(f"Agency:   {opp.get('fullParentPathName', '').split('.')[-1].strip()}")
        print(f"Posted:   {opp.get('postedDate')}")
        print(f"Deadline: {opp.get('responseDeadLine')}")
        print(f"Link:     {opp.get('uiLink')}")
        print("-" * 60)

except requests.exceptions.Timeout:
    print("Timed out.")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")