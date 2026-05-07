#!/usr/bin/env python3
"""
ParikshaMitra — Govt Jobs Fetcher
Har 6 ghante chalega, jobs.json update karega
"""

import os, json, requests, re
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST).strftime("%Y-%m-%d")

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
DATA_FILE = "data/jobs.json"

JOB_QUERIES = [
    "SSC recruitment 2025 vacancy notification",
    "UPSC recruitment notification 2025",
    "Railway RRB recruitment 2025 vacancy",
    "IBPS SBI bank recruitment 2025",
    "government job vacancy 2025 India",
    "police constable recruitment 2025",
    "army navy airforce recruitment 2025",
    "state government job vacancy 2025",
]

EXAM_PATTERNS = {
    "SSC": r"SSC|Staff Selection",
    "UPSC": r"UPSC|civil services|IAS|IPS",
    "Railway": r"railway|RRB|RRC|NTPC",
    "Bank": r"IBPS|SBI|RBI|bank",
    "Police": r"police|constable",
    "Defence": r"army|navy|airforce|military|CDS|NDA",
    "State": r"state|UP|MP|Bihar|Rajasthan|Maharashtra",
}

def detect_exam(text):
    text_upper = text.upper()
    for exam, pattern in EXAM_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return exam
    return "General"

def detect_vacancies(text):
    patterns = [
        r'(\d{2,6})\s*(?:posts?|vacancies|seats|positions)',
        r'(?:posts?|vacancies)\s*(?:of|:)?\s*(\d{2,6})',
        r'recruit(?:ing|ment)?\s*(\d{2,6})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "See notification"

def load_existing():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"jobs": [], "lastUpdated": ""}

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data['jobs'])} jobs")

def fetch_jobs():
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY nahi hai!")
        return load_existing()

    existing_data = load_existing()
    existing_titles = {j["title"] for j in existing_data["jobs"]}
    new_jobs = []
    next_id = max((j["id"] for j in existing_data["jobs"]), default=0) + 1

    for query in JOB_QUERIES:
        try:
            res = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 3,
                    "apiKey": NEWS_API_KEY
                },
                timeout=10
            )
            articles = res.json().get("articles", [])

            for article in articles:
                title = (article.get("title") or "").strip()
                if not title or title == "[Removed]" or title in existing_titles:
                    continue
                if len(title) < 15:
                    continue

                full_text = title + " " + (article.get("description") or "")
                exam = detect_exam(full_text)
                vacancies = detect_vacancies(full_text)

                # Last date — 30 days from today (approximate)
                last_date = datetime.now(IST) + timedelta(days=30)

                job = {
                    "id": next_id,
                    "title": title[:100],
                    "org": article.get("source", {}).get("name", "Govt of India"),
                    "lastDate": last_date.strftime("%Y-%m-%d"),
                    "lastDateDisplay": last_date.strftime("%d %b %Y"),
                    "vacancies": vacancies,
                    "link": article.get("url", "#"),
                    "exam": exam,
                    "type": "new",
                    "category": "central",
                    "addedDate": TODAY,
                    "auto": True
                }

                new_jobs.append(job)
                existing_titles.add(title)
                next_id += 1

        except Exception as e:
            print(f"❌ Error: {e}")

    if new_jobs:
        existing_data["jobs"] = new_jobs + existing_data["jobs"]
        existing_data["jobs"] = existing_data["jobs"][:200]
        existing_data["lastUpdated"] = TODAY
        print(f"💼 {len(new_jobs)} nayi jobs add ki!")
    else:
        print("ℹ️ Koi nayi job nahi mili.")

    return existing_data

if __name__ == "__main__":
    print(f"💼 Govt jobs check ho rahi hain — {TODAY}")
    data = fetch_jobs()
    save_data(data)
    print("✅ Done!")

