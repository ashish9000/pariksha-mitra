#!/usr/bin/env python3
"""ParikshaMitra — Monthly Summary Generator"""

import os, json
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime.now(IST)

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def create_monthly_summary():
    affairs = load_json("data/affairs.json").get("affairs", [])
    jobs = load_json("data/jobs.json").get("jobs", [])
    quizzes = load_json("data/quiz.json").get("quizzes", [])

    month = NOW.strftime("%B %Y")
    month_prefix = NOW.strftime("%Y-%m")

    # Is mahine ki affairs
    month_affairs = [a for a in affairs if a.get("date", "").startswith(month_prefix)]

    # Categories count
    cats = {}
    for a in month_affairs:
        c = a.get("category", "Other")
        cats[c] = cats.get(c, 0) + 1

    summary = {
        "month": month,
        "generatedOn": NOW.strftime("%Y-%m-%d"),
        "stats": {
            "totalAffairs": len(month_affairs),
            "totalJobs": len(jobs),
            "totalQuizzes": len(quizzes),
            "categoriesBreakdown": cats
        },
        "topAffairs": month_affairs[:20],  # Top 20 is mahine ki
        "newJobs": [j for j in jobs if j.get("addedDate", "").startswith(month_prefix)][:10]
    }

    filename = f"data/monthly_{NOW.strftime('%Y_%m')}.json"
    save_json(filename, summary)
    print(f"📊 Monthly summary saved: {filename}")
    print(f"   Affairs: {len(month_affairs)}, Jobs: {len(jobs)}, Quizzes: {len(quizzes)}")

    # Clean 6 mahine purana daily data
    cutoff = NOW - timedelta(days=180)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    affairs_data = load_json("data/affairs.json")
    all_affairs = affairs_data.get("affairs", [])
    cleaned = [a for a in all_affairs if a.get("date", "9999") > cutoff_str or a.get("period") != "daily"]
    removed = len(all_affairs) - len(cleaned)
    if removed > 0:
        affairs_data["affairs"] = cleaned
        save_json("data/affairs.json", affairs_data)
        print(f"🧹 {removed} purani entries clean ki gayi")

if __name__ == "__main__":
    create_monthly_summary()
    print("✅ Monthly tasks done!")

