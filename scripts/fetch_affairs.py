#!/usr/bin/env python3
"""
ParikshaMitra — Daily Current Affairs Fetcher
Roz automatically chalega, affairs.json update karega
"""

import os, json, requests
from datetime import datetime, timezone, timedelta

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST).strftime("%Y-%m-%d")
TODAY_DISPLAY = datetime.now(IST).strftime("%d %b %Y")

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

DATA_FILE = "data/affairs.json"

# ─── News Topics ───────────────────────────────────────────
TOPICS = [
    {"query": "India government scheme policy announcement", "category": "National",       "cat_hi": "राष्ट्रीय"},
    {"query": "India economy RBI finance budget",           "category": "Economy",         "cat_hi": "अर्थव्यवस्था"},
    {"query": "India science technology ISRO space",        "category": "Science",         "cat_hi": "विज्ञान"},
    {"query": "India sports cricket Olympics medal",        "category": "Sports",          "cat_hi": "खेल"},
    {"query": "India international diplomacy summit",       "category": "International",   "cat_hi": "अंतर्राष्ट्रीय"},
    {"query": "India environment climate disaster",         "category": "Environment",     "cat_hi": "पर्यावरण"},
]

# ─── Load Existing Data ────────────────────────────────────
def load_existing():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"affairs": [], "lastUpdated": ""}

# ─── Save Data ─────────────────────────────────────────────
def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(data['affairs'])} affairs to {DATA_FILE}")

# ─── Hindi Translation via Claude ─────────────────────────
def translate_to_hindi(title_en, content_en):
    if not CLAUDE_API_KEY:
        return title_en, content_en

    prompt = f"""Translate this news to simple Hindi for competitive exam students (SSC/UPSC).
Return ONLY JSON, no markdown, no extra text.

Title: "{title_en}"
Content: "{content_en}"

Format: {{"titleHi": "...", "contentHi": "..."}}"""

    try:
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": CLAUDE_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        data = res.json()
        text = data["content"][0]["text"].strip()
        parsed = json.loads(text)
        return parsed.get("titleHi", title_en), parsed.get("contentHi", content_en)
    except Exception as e:
        print(f"⚠️ Hindi translation failed: {e}")
        return title_en, content_en

# ─── Fetch News ────────────────────────────────────────────
def fetch_news():
    if not NEWS_API_KEY:
        print("⚠️ NEWS_API_KEY nahi hai! Sample data use ho raha hai.")
        return get_sample_affairs()

    existing_data = load_existing()
    existing_titles = {a["title"] for a in existing_data["affairs"]}
    new_items = []
    next_id = max((a["id"] for a in existing_data["affairs"]), default=0) + 1

    for topic in TOPICS:
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": topic["query"],
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 3,
                "from": TODAY,
                "apiKey": NEWS_API_KEY
            }
            res = requests.get(url, params=params, timeout=10)
            articles = res.json().get("articles", [])

            for article in articles:
                title = (article.get("title") or "").strip()
                if not title or title == "[Removed]":
                    continue
                if title in existing_titles:
                    continue
                if len(title) < 20:
                    continue

                content = (article.get("description") or "")[:300].strip()
                title_en = title[:120]

                print(f"  🔄 Translating: {title_en[:50]}...")
                title_hi, content_hi = translate_to_hindi(title_en, content)

                item = {
                    "id": next_id,
                    "date": TODAY,
                    "dateDisplay": TODAY_DISPLAY,
                    "title": title_en,
                    "titleHi": title_hi,
                    "content": content,
                    "contentHi": content_hi,
                    "category": topic["category"],
                    "categoryHi": topic["cat_hi"],
                    "period": "daily",
                    "link": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "News"),
                    "auto": True
                }

                new_items.append(item)
                existing_titles.add(title)
                next_id += 1

        except Exception as e:
            print(f"❌ Error fetching {topic['category']}: {e}")

    if new_items:
        # Naye items pehle
        existing_data["affairs"] = new_items + existing_data["affairs"]
        # 500 se zyada mat rakhna
        existing_data["affairs"] = existing_data["affairs"][:500]
        existing_data["lastUpdated"] = TODAY
        print(f"📰 {len(new_items)} nayi khabrein add ki!")
    else:
        print("ℹ️ Koi nayi khabar nahi mili.")

    return existing_data

# ─── Sample Data (jab API na ho) ──────────────────────────
def get_sample_affairs():
    return {
        "affairs": [
            {
                "id": 1,
                "date": TODAY,
                "dateDisplay": TODAY_DISPLAY,
                "title": "PM announces new infrastructure scheme for rural India",
                "titleHi": "PM ने ग्रामीण भारत के लिए नई इंफ्रास्ट्रक्चर योजना की घोषणा की",
                "content": "The Prime Minister announced a new scheme focusing on rural road connectivity.",
                "contentHi": "प्रधानमंत्री ने ग्रामीण सड़क संपर्क पर केंद्रित एक नई योजना की घोषणा की।",
                "category": "National",
                "categoryHi": "राष्ट्रीय",
                "period": "daily",
                "link": "",
                "source": "Sample",
                "auto": False
            }
        ],
        "lastUpdated": TODAY
    }

# ─── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"📰 Current Affairs fetch ho rahi hain — {TODAY_DISPLAY}")
    data = fetch_news()
    save_data(data)
    print("✅ Done!")

