import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
import os
import re
import csv

SOURCES = [
    # Co-op purchasing
    {
        "name": "ESCNJ Bidding Opportunities",
        "url": "https://www.escnj.us/co-op-pricing/vendor-section/bidding-opportunity-documents",
        "escnj": True
    },
    # Mercer County school districts
    {
        "name": "Princeton Public Schools",
        "url": "https://www.princetonk12.org/resources-and-notices/rfps-bids-and-quotes",
        "escnj": False
    },
    {
        "name": "East Windsor Regional SD",
        "url": "https://www.ewrsd.org/domain/29",
        "escnj": False
    },
    {
        "name": "Hopewell Valley Regional SD",
        "url": "https://www.hvrsd.org/domain/54",
        "escnj": False
    },
    {
        "name": "Lawrence Township Schools",
        "url": "https://www.ltps.org/departments/business-office",
        "escnj": False
    },
    # Mercer County municipalities
    {
        "name": "Princeton NJ Borough Bids",
        "url": "https://www.princetonnj.gov/Bids.aspx",
        "escnj": False
    },
    {
        "name": "Lawrence Township NJ Bids",
        "url": "https://www.lawrencetwp.com/CurrentBidsRFPs",
        "escnj": False
    },
    # Middlesex County school districts
    {
        "name": "Monroe Township Schools",
        "url": "https://www.monroe.k12.nj.us/our-district/business-office/overview",
        "escnj": False
    },
    {
        "name": "South Brunswick Schools",
        "url": "https://www.sbschools.org/departments/business_office",
        "escnj": False
    },
    {
        "name": "Piscataway Township Schools",
        "url": "https://www.piscatawayschools.org/79055_3",
        "escnj": False
    },
    {
        "name": "Edison Township Schools",
        "url": "https://www.edison.k12.nj.us/departments/business_office",
        "escnj": False
    },
]

IT_KEYWORDS = [
    "information technology", "it support", "managed services",
    "cybersecurity", "network", "helpdesk", "cloud services",
    "computer repair", "device repair", "hardware support",
    "internet access", "data transmission", "technology consulting",
    "wifi", "wireless network", "software support", "tech support",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

CSV_FILE = "/Users/kritinrane/Documents/governmentscraper-nerdstogo/leads.csv"

def is_it_related(text):
    return any(kw in text.lower() for kw in IT_KEYWORDS)

def is_current(text):
    return bool(re.search(r'2[34567]/2[4567]|25/26|26/27|24/25|23/24', text))

def scrape_source(source):
    hits = []
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        if source["escnj"]:
            for tag in soup.find_all("a"):
                text = tag.get_text(strip=True)
                if not (len(text) > 30 and is_it_related(text) and is_current(text)):
                    continue
                href = tag.get("href", "")
                link = href if href.startswith("http") else "https://www.escnj.us" + href
                hits.append({
                    "source": source["name"],
                    "text": text[:200],
                    "link": link
                })
        else:
            for tag in soup.find_all("a"):
                text = tag.get_text(strip=True)
                if not (len(text) > 30 and is_it_related(text)):
                    continue
                href = tag.get("href", "")
                if href:
                    base = "/".join(source["url"].split("/")[:3])
                    link = href if href.startswith("http") else base + "/" + href.lstrip("/")
                else:
                    link = ""
                hits.append({
                    "source": source["name"],
                    "text": text[:200],
                    "link": link
                })

    except Exception as e:
        print(f"  ERROR on {source['name']}: {e}")

    return hits

def load_seen():
    if os.path.exists("seen_bids.json"):
        with open("seen_bids.json") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open("seen_bids.json", "w") as f:
        json.dump(list(seen), f)

def save_to_csv(hits):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "source", "text", "link"])
        if not file_exists:
            writer.writeheader()
        for hit in hits:
            writer.writerow({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source": hit["source"],
                "text": hit["text"],
                "link": hit["link"]
            })
    print(f"Saved {len(hits)} new hits to leads.csv")

def send_email(new_hits, to_email, from_email, app_password):
    if not new_hits:
        print("No new hits to email.")
        return

    body = f"New IT-related government opportunities found on {datetime.now().strftime('%Y-%m-%d')}:\n\n"
    for hit in new_hits:
        body += f"SOURCE: {hit['source']}\n"
        body += f"TEXT:   {hit['text']}\n"
        body += f"LINK:   {hit['link']}\n"
        body += "-" * 60 + "\n"

    msg = MIMEText(body)
    msg["Subject"] = f"[NerdsToGo] {len(new_hits)} New IT Bid(s) Found"
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, app_password)
        server.sendmail(from_email, to_email, msg.as_string())

    print(f"Email sent with {len(new_hits)} new hits.")

def main():
    seen = load_seen()
    all_hits = []

    for source in SOURCES:
        print(f"Scraping {source['name']}...")
        hits = scrape_source(source)
        all_hits.extend(hits)
        print(f"  Found {len(hits)} IT-related items")

    new_hits = []
    for hit in all_hits:
        key = hit["source"] + hit["text"][:50]
        if key not in seen:
            new_hits.append(hit)
            seen.add(key)

    save_seen(seen)

    print(f"\nTotal new hits: {len(new_hits)}\n")
    for hit in new_hits:
        print(f"[{hit['source']}]")
        print(f"  {hit['text'][:120]}")
        if hit["link"]:
            print(f"  -> {hit['link']}")
        print()

    if new_hits:
        save_to_csv(new_hits)

    send_email(
        new_hits=new_hits,
        to_email=os.environ.get("to_email"),
        from_email=os.environ.get("from_email"),
        app_password=os.environ.get("app_password")
    )


if __name__ == "__main__":
    main()