#!/usr/bin/env python3
"""
ParikshaMitra — Email Notification Script
Gmail SMTP se daily/weekly/monthly summary email
"""

import os, sys, json, smtplib
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

IST = timezone(timedelta(hours=5, minutes=30))
NOW = datetime.now(IST)
TODAY = NOW.strftime("%d %b %Y")

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "shishgupt9000@gmail.com")
GMAIL_USER  = os.environ.get("GMAIL_USER", "")
GMAIL_PASS  = os.environ.get("GMAIL_PASS", "")  # Gmail App Password

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def send_email(subject, html_body):
    if not GMAIL_USER or not GMAIL_PASS:
        print("⚠️ Gmail credentials nahi hain — email skip")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_USER
        msg["To"]      = ADMIN_EMAIL

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, ADMIN_EMAIL, msg.as_string())

        print(f"✅ Email bheja: {ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def daily_email():
    affairs = load_json("data/affairs.json").get("affairs", [])
    jobs    = load_json("data/jobs.json").get("jobs", [])
    today_str = NOW.strftime("%Y-%m-%d")
    today_news = [a for a in affairs if a.get("date") == today_str]
    today_jobs = [j for j in jobs if j.get("addedDate") == today_str]

    news_rows = "".join([f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:13px;">{a.get('titleHi') or a.get('title','')}</td>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:11px;color:#8BA7C7;">{a.get('category','')}</td>
        </tr>""" for a in today_news[:10]])

    jobs_rows = "".join([f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:13px;">{j.get('title','')}</td>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:11px;color:#8BA7C7;">{j.get('lastDate','')}</td>
          <td style="padding:8px;border-bottom:1px solid #1A3055;">
            <a href="{j.get('link','#')}" style="color:#FF6B00;font-size:11px;">Apply →</a>
          </td>
        </tr>""" for j in today_jobs[:5]])

    html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0A1628;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#FF6B00,#FF8C38);border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">
      <h1 style="color:white;margin:0;font-size:24px;">📚 ParikshaMitra</h1>
      <p style="color:rgba(255,255,255,0.9);margin:6px 0 0;font-size:14px;">Daily Update — {TODAY}</p>
    </div>

    <!-- Stats -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
      <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:800;color:#FF6B00;">{len(today_news)}</div>
        <div style="font-size:12px;color:#8BA7C7;margin-top:4px;">News Added</div>
      </div>
      <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;text-align:center;">
        <div style="font-size:28px;font-weight:800;color:#00D4A0;">{len(today_jobs)}</div>
        <div style="font-size:12px;color:#8BA7C7;margin-top:4px;">Jobs Added</div>
      </div>
    </div>

    <!-- News Table -->
    <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <h3 style="color:#F0F6FF;margin:0 0 12px;font-size:15px;">📰 Aaj ki Top News</h3>
      <table style="width:100%;border-collapse:collapse;">
        <tr style="background:rgba(255,107,0,0.1);">
          <th style="padding:8px;text-align:left;font-size:12px;color:#8BA7C7;">Headline</th>
          <th style="padding:8px;text-align:left;font-size:12px;color:#8BA7C7;">Category</th>
        </tr>
        {news_rows if news_rows else '<tr><td colspan="2" style="padding:16px;text-align:center;color:#8BA7C7;font-size:13px;">Koi nayi khabar nahi</td></tr>'}
      </table>
    </div>

    <!-- Jobs Table -->
    <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <h3 style="color:#F0F6FF;margin:0 0 12px;font-size:15px;">💼 New Job Alerts</h3>
      <table style="width:100%;border-collapse:collapse;">
        <tr style="background:rgba(0,212,160,0.1);">
          <th style="padding:8px;text-align:left;font-size:12px;color:#8BA7C7;">Job</th>
          <th style="padding:8px;text-align:left;font-size:12px;color:#8BA7C7;">Last Date</th>
          <th style="padding:8px;text-align:left;font-size:12px;color:#8BA7C7;">Link</th>
        </tr>
        {jobs_rows if jobs_rows else '<tr><td colspan="3" style="padding:16px;text-align:center;color:#8BA7C7;font-size:13px;">Koi nayi job nahi</td></tr>'}
      </table>
    </div>

    <!-- Action Buttons -->
    <div style="text-align:center;margin-bottom:20px;">
      <a href="https://ashish9000.github.io/ParikshaMitra/admin.html"
         style="display:inline-block;background:linear-gradient(135deg,#FF6B00,#FF8C38);color:white;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;margin:5px;">
        🔧 Admin Panel
      </a>
      <a href="https://ashish9000.github.io/ParikshaMitra"
         style="display:inline-block;background:linear-gradient(135deg,#00D4A0,#00A880);color:#0A1628;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;margin:5px;">
        📱 Live App
      </a>
    </div>

    <!-- Footer -->
    <div style="text-align:center;color:#8BA7C7;font-size:11px;padding-top:16px;border-top:1px solid rgba(255,107,0,0.1);">
      ParikshaMitra Bot • Auto-generated • {TODAY}
    </div>
  </div>
</body>
</html>"""

    send_email(f"📚 ParikshaMitra Daily Update — {TODAY}", html)

def weekly_email():
    quiz = load_json("data/quiz.json")
    total_q = sum(len(v) for v in quiz.get("questions", {}).values())
    quizzes = quiz.get("quizzes", [])

    rows = "".join([f"""
        <tr>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:13px;">{q.get('titleHi') or q.get('title','')}</td>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:12px;color:#8BA7C7;">{q.get('exam','')}</td>
          <td style="padding:8px;border-bottom:1px solid #1A3055;font-size:12px;color:#FF6B00;">{q.get('questions',0)} Qs</td>
        </tr>""" for q in quizzes[:10]])

    html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0A1628;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:linear-gradient(135deg,#7C6FF7,#9B88FF);border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">
      <h1 style="color:white;margin:0;font-size:24px;">📝 Weekly Quiz Update</h1>
      <p style="color:rgba(255,255,255,0.9);margin:6px 0 0;font-size:14px;">{TODAY}</p>
    </div>

    <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;margin-bottom:16px;text-align:center;">
      <div style="font-size:36px;font-weight:800;color:#FF6B00;">{total_q}</div>
      <div style="font-size:13px;color:#8BA7C7;">Total Questions Generated</div>
    </div>

    <div style="background:#112240;border:1px solid rgba(255,107,0,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <h3 style="color:#F0F6FF;margin:0 0 12px;font-size:15px;">📋 Quiz Subjects</h3>
      <table style="width:100%;border-collapse:collapse;">
        {rows}
      </table>
    </div>

    <div style="text-align:center;">
      <a href="https://ashish9000.github.io/ParikshaMitra/admin.html"
         style="display:inline-block;background:linear-gradient(135deg,#FF6B00,#FF8C38);color:white;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;">
        ✅ Review Questions
      </a>
    </div>
  </div>
</body>
</html>"""

    send_email(f"📝 ParikshaMitra Weekly Quiz — {TODAY}", html)

def monthly_email():
    affairs = load_json("data/affairs.json").get("affairs", [])
    jobs    = load_json("data/jobs.json").get("jobs", [])
    quiz    = load_json("data/quiz.json")
    total_q = sum(len(v) for v in quiz.get("questions", {}).values())
    month   = NOW.strftime("%B %Y")

    html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0A1628;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:16px;padding:24px;text-align:center;margin-bottom:20px;">
      <h1 style="color:#0A1628;margin:0;font-size:24px;">📊 Monthly Report</h1>
      <p style="color:rgba(0,0,0,0.7);margin:6px 0 0;font-size:14px;">{month}</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px;">
      <div style="background:#112240;border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:24px;font-weight:800;color:#FF6B00;">{len(affairs)}</div>
        <div style="font-size:11px;color:#8BA7C7;margin-top:3px;">Total Articles</div>
      </div>
      <div style="background:#112240;border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:24px;font-weight:800;color:#00D4A0;">{len(jobs)}</div>
        <div style="font-size:11px;color:#8BA7C7;margin-top:3px;">Job Alerts</div>
      </div>
      <div style="background:#112240;border-radius:12px;padding:14px;text-align:center;">
        <div style="font-size:24px;font-weight:800;color:#7C6FF7;">{total_q}</div>
        <div style="font-size:11px;color:#8BA7C7;margin-top:3px;">Questions</div>
      </div>
    </div>

    <div style="background:#112240;border:1px solid rgba(255,215,0,0.2);border-radius:12px;padding:16px;margin-bottom:16px;">
      <h3 style="color:#FFD700;margin:0 0 10px;">📋 Action Required</h3>
      <ul style="color:#F0F6FF;font-size:13px;line-height:2;padding-left:16px;">
        <li>Expired jobs remove karo admin panel se</li>
        <li>Exam dates verify aur update karo</li>
        <li>Next month ke exams add karo</li>
        <li>Monthly current affairs PDF students ke liye</li>
      </ul>
    </div>

    <div style="text-align:center;">
      <a href="https://ashish9000.github.io/ParikshaMitra/admin.html"
         style="display:inline-block;background:linear-gradient(135deg,#FFD700,#FFA500);color:#0A1628;padding:14px 28px;border-radius:10px;text-decoration:none;font-weight:800;font-size:15px;">
        🔧 Open Admin Panel
      </a>
    </div>
  </div>
</body>
</html>"""

    send_email(f"📊 ParikshaMitra Monthly Report — {month}", html)

# ─── Main ──────────────────────────────────────────────────
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    print(f"📧 Email bhej raha hoon: {mode}")

    if mode == "daily":   daily_email()
    elif mode == "weekly": weekly_email()
    elif mode == "monthly": monthly_email()

    print("✅ Done!")
