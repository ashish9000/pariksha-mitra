#!/usr/bin/env python3
"""
ParikshaMitra — Notification Script
Telegram + Email alerts after every AI update
"""

import os, sys, json, requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime.now(IST)
TODAY = NOW.strftime("%d %b %Y")
TIME  = NOW.strftime("%I:%M %p")

TG_TOKEN  = os.environ.get("TG_TOKEN", "")
TG_CHAT   = os.environ.get("TG_CHAT_ID", "")

def send_telegram(msg):
    if not TG_TOKEN or not TG_CHAT:
        print("⚠️ Telegram credentials nahi hain")
        return False
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
        data = res.json()
        if data.get("ok"):
            print("✅ Telegram notification bheja!")
            return True
        else:
            print(f"❌ Telegram error: {data}")
            return False
    except Exception as e:
        print(f"❌ Telegram exception: {e}")
        return False

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def daily_notification():
    affairs = load_json("data/affairs.json").get("affairs", [])
    jobs    = load_json("data/jobs.json").get("jobs", [])

    # Aaj ki news count
    today_str = NOW.strftime("%Y-%m-%d")
    today_news = [a for a in affairs if a.get("date") == today_str]
    today_jobs = [j for j in jobs if j.get("addedDate") == today_str]

    # Top 5 news headlines
    headlines = ""
    for i, a in enumerate(today_news[:5], 1):
        title = a.get("titleHi") or a.get("title", "")
        headlines += f"\n{i}. {title[:80]}"

    msg = f"""📚 <b>ParikshaMitra Daily Update</b>
📅 {TODAY} | ⏰ {TIME} IST

📰 <b>Aaj ki News:</b> {len(today_news)} articles added
💼 <b>New Jobs:</b> {len(today_jobs)} jobs added

<b>Top Headlines:</b>{headlines if headlines else "\nKoi nayi khabar nahi"}

🔔 <b>Action Required:</b>
• Jobs verify karo — apply links check karo
• Galat news remove karo agar ho

👉 Admin Panel: <a href="https://ashish9000.github.io/ParikshaMitra/admin.html">Open Admin</a>
👉 Live App: <a href="https://ashish9000.github.io/ParikshaMitra">Open App</a>"""

    send_telegram(msg)

def weekly_notification():
    quiz = load_json("data/quiz.json")
    quizzes  = quiz.get("quizzes", [])
    questions = quiz.get("questions", {})
    total_q = sum(len(v) for v in questions.values())

    # Subject breakdown
    breakdown = ""
    for key, qs in list(questions.items())[:5]:
        breakdown += f"\n• {key.replace('_',' ')}: {len(qs)} questions"

    msg = f"""📝 <b>ParikshaMitra Weekly Quiz Update</b>
📅 {TODAY} | ⏰ {TIME} IST

✅ <b>Quiz Questions Generated!</b>
📊 Total Quizzes: {len(quizzes)}
❓ Total Questions: {total_q}

<b>Subjects Updated:</b>{breakdown}

🔔 <b>Action Required:</b>
• Questions review karo — galat answers check karo
• Weekly 10 min review recommended

👉 Admin Panel: <a href="https://ashish9000.github.io/ParikshaMitra/admin.html">Review Content</a>"""

    send_telegram(msg)

def monthly_notification():
    affairs  = load_json("data/affairs.json").get("affairs", [])
    jobs     = load_json("data/jobs.json").get("jobs", [])
    quiz     = load_json("data/quiz.json")
    total_q  = sum(len(v) for v in quiz.get("questions", {}).values())
    month    = NOW.strftime("%B %Y")

    msg = f"""📊 <b>ParikshaMitra Monthly Report</b>
📅 {month}

✅ <b>Automation Summary:</b>
📰 Current Affairs: {len(affairs)} total articles
💼 Job Alerts: {len(jobs)} total jobs
📝 Quiz Questions: {total_q} total questions

🧹 Purana data cleanup complete
📦 Monthly archive saved

🔔 <b>Action Required:</b>
• Expired jobs remove karo
• Exam dates update karo
• Monthly current affairs PDF banao

👉 Admin Panel: <a href="https://ashish9000.github.io/ParikshaMitra/admin.html">Open Admin</a>"""

    send_telegram(msg)

def new_job_alert(job_title, org, vacancies, last_date, apply_link):
    """Jab bhi nayi job add ho — instant alert"""
    msg = f"""🆕 <b>New Job Alert!</b>

🎯 <b>{job_title}</b>
🏛️ {org}
👥 {vacancies} Vacancies
📅 Last Date: {last_date}
🔗 Apply: {apply_link}

⚠️ Verify karo apply link correct hai!
👉 <a href="https://ashish9000.github.io/ParikshaMitra/admin.html">Admin Panel</a>"""

    send_telegram(msg)

def exam_deadline_alert(exam_name, days_left, apply_link):
    """Exam deadline ke 7 aur 3 din pehle alert"""
    emoji = "🚨" if days_left <= 3 else "⚠️"
    msg = f"""{emoji} <b>Exam Deadline Alert!</b>

📅 <b>{exam_name}</b>
⏰ Sirf <b>{days_left} din</b> bache hain!

🔗 Apply Link: {apply_link}

Students ko remind karo!"""

    send_telegram(msg)

# ─── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"

    if mode == "daily":
        print("📱 Daily notification bhej raha hoon...")
        daily_notification()
    elif mode == "weekly":
        print("📱 Weekly notification bhej raha hoon...")
        weekly_notification()
    elif mode == "monthly":
        print("📱 Monthly notification bhej raha hoon...")
        monthly_notification()
    else:
        print(f"❌ Unknown mode: {mode}")

    print("✅ Done!")
