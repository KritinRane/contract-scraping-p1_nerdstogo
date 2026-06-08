# 🖥️ NerdsToGo Princeton — Government IT Bid Scraper

An automated lead generation pipeline that scrapes NJ school districts, municipalities, and co-op purchasing programs for IT-related contract opportunities. Built for **NerdsToGo Princeton** (Plainsboro, NJ) to surface actionable government IT bids daily by intern: Kritin Rane. 

---

## 📋 Overview

This project consists of two scrapers:

| File | Purpose |
|------|---------|
| `samGov.py` | Scrapes federal contracts from the SAM.gov API |
| `education.py` | Scrapes NJ local government and school district bid portals |

> **Note:** After research, federal contracts via SAM.gov were determined to be misaligned with a local IT franchise. The primary scraper is `education.py` targeting local NJ government entities.

---

## 🎯 Target Sources

### Co-op Purchasing
- **ESCNJ** (Educational Services Commission of NJ) — co-op contracts used by hundreds of NJ school districts

### Mercer County School Districts
- Princeton Public Schools
- East Windsor Regional SD
- Hopewell Valley Regional SD
- Lawrence Township Public Schools

### Mercer County Municipalities
- Princeton Borough
- Lawrence Township

### Middlesex County School Districts
- Monroe Township Schools
- South Brunswick Schools
- Piscataway Township Schools
- Edison Township Schools

---

## ⚙️ How It Works

1. Scrapes each source daily for IT-related bid listings
2. Compares results against `seen_bids.json` to identify new listings only
3. Saves new hits to `leads.csv` with date, source, description, and link
4. Sends an email alert to the NerdsToGo inbox when new opportunities are found

### IT Keyword Matching
The scraper filters results using these keywords:
```
information technology, it support, managed services, cybersecurity,
network, helpdesk, cloud services, computer repair, device repair,
hardware support, internet access, data transmission, technology
consulting, wifi, wireless network, software support, tech support
```

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/KritinRane/nerdstogoProj.git
cd nerdstogoProj
```

### 2. Install dependencies
```bash
pip install requests beautifulsoup4 python-dotenv --break-system-packages
```

### 3. Create your `.env` file
```bash
touch .env
```

Add the following to `.env`:
```
SAM_API_KEY=your_sam_gov_api_key
TO_EMAIL=your@email.com
FROM_EMAIL=yourbot@gmail.com
APP_PASSWORD=your_gmail_app_password
```

> **Never commit your `.env` file.** It is listed in `.gitignore`.

### 4. Get a Gmail App Password
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → App Passwords
3. Create a new app password and paste it into `.env`

### 5. Get a SAM.gov API Key (for `samGov.py` only)
1. Register at [sam.gov](https://sam.gov)
2. Go to Account Details → Request Public API Key

---

## 🏃 Running the Scraper

```bash
python3 education.py
```

### Example output
```
Scraping ESCNJ Bidding Opportunities...
  Found 4 IT-related items
Scraping Princeton Public Schools...
  Found 0 IT-related items
...
Total new hits: 2

[ESCNJ Bidding Opportunities]
  INTERNET ACCESS AND DATA TRANSMISSION SERVICES - RFP ESCNJ 23/24-19
  -> https://www.escnj.us/...
```

---

## ⏰ Automating with Cron (macOS)

Run the scraper every morning at 8am:

```bash
crontab -e
```

Add this line (replace Python path if needed):
```
0 8 * * * /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 /Users/yourname/Documents/governmentscraper-nerdstogo/education.py >> /Users/yourname/Documents/governmentscraper-nerdstogo/scraper.log 2>&1
```

Verify it was saved:
```bash
crontab -l
```

Check logs:
```bash
cat scraper.log
```

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `seen_bids.json` | Tracks previously seen bids to avoid duplicate alerts |
| `leads.csv` | Running log of all new IT leads found, with date, source, description, and link |
| `scraper.log` | Cron job output log |

---

## 🔒 Security Notes

- All credentials are stored in `.env` and never committed to GitHub
- `.env` is listed in `.gitignore`
- Gmail App Passwords are used instead of your actual Gmail password

---

## 🏢 About

Built for **NerdsToGo Princeton**
666 Plainsboro Rd, Building 400 Suite #405
Plainsboro, NJ 08536
(732) 808-2946

NerdsToGo provides computer repair, device repair, network setup, IT support, and technology consulting services to businesses and organizations throughout Mercer and Middlesex counties.

---

## 📬 Contact

For questions about this project, reach out to the NerdsToGo Princeton team at [Kritin.Rane@nerdstogo.com](mailto:Kritin.Rane@nerdstogo.com)
