#!/usr/bin/env python3
"""
ParikshaMitra — AI Quiz Question Generator
Har Sunday chalega, naye questions add karega
"""

import os, json, requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST).strftime("%Y-%m-%d")

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
DATA_FILE = "data/quiz.json"

TOPICS = [
    {"exam": "SSC",     "subject": "General Knowledge", "subjectHi": "सामान्य ज्ञान",   "count": 5},
    {"exam": "SSC",     "subject": "Mathematics",        "subjectHi": "गणित",             "count": 5},
    {"exam": "SSC",     "subject": "Hindi Grammar",      "subjectHi": "हिंदी व्याकरण",    "count": 5},
    {"exam": "UPSC",    "subject": "Polity",             "subjectHi": "राजव्यवस्था",      "count": 5},
    {"exam": "UPSC",    "subject": "History",            "subjectHi": "इतिहास",           "count": 5},
    {"exam": "Railway", "subject": "Reasoning",          "subjectHi": "तर्कशक्ति",        "count": 5},
    {"exam": "Railway", "subject": "General Science",    "subjectHi": "सामान्य विज्ञान",  "count": 5},
    {"exam": "Bank",    "subject": "English",            "subjectHi": "अंग्रेजी",         "count": 5},
    {"exam": "Bank",    "subject": "Reasoning",          "subjectHi": "तर्कशक्ति",        "count": 5},
]

SAMPLE_QUESTIONS = {
    "SSC_General Knowledge": [
        {"question":"Which is the national animal of India?","questionHi":"भारत का राष्ट्रीय पशु कौन सा है?","optA":"Lion","optB":"Tiger","optC":"Elephant","optD":"Leopard","answer":"B","difficulty":"Easy","explanation":"Bengal Tiger is India's national animal since 1973."},
        {"question":"Who wrote the Indian National Anthem?","questionHi":"भारतीय राष्ट्रगान किसने लिखा?","optA":"Bankim Chandra","optB":"Rabindranath Tagore","optC":"Subhash Bose","optD":"Gandhi","answer":"B","difficulty":"Easy","explanation":"Jana Gana Mana was written by Rabindranath Tagore."},
    ],
    "Railway_Reasoning": [
        {"question":"Series: 2, 6, 12, 20, 30, ?","questionHi":"श्रृंखला: 2, 6, 12, 20, 30, ?","optA":"40","optB":"42","optC":"44","optD":"46","answer":"B","difficulty":"Medium","explanation":"Differences are 4,6,8,10,12 — next is 42."},
        {"question":"If DELHI = 73541, then HIDE = ?","questionHi":"यदि DELHI = 73541, तो HIDE = ?","optA":"4573","optB":"5473","optC":"4537","optD":"5374","answer":"C","difficulty":"Hard","explanation":"D=7,E=3,L=5,H=4,I=1 so HIDE=4153... mapping ke anusar."},
    ],
}

def load_existing():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"quizzes": [], "questions": {}, "lastUpdated": ""}

def save_data(data):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Quiz data saved!")

def generate_with_claude(exam, subject, count):
    if not CLAUDE_API_KEY:
        key = f"{exam}_{subject}"
        return SAMPLE_QUESTIONS.get(key, SAMPLE_QUESTIONS["SSC_General Knowledge"])[:count]

    prompt = f"""Generate {count} multiple choice questions for Indian competitive exam ({exam}) on: {subject}.

Important:
- Questions should match {exam} exam pattern and difficulty
- Include Hindi translation of each question
- Mix Easy/Medium/Hard questions
- Return ONLY valid JSON array, no markdown, no extra text

[
  {{
    "question": "Question in English",
    "questionHi": "Question in Hindi",
    "optA": "Option A",
    "optB": "Option B",
    "optC": "Option C", 
    "optD": "Option D",
    "answer": "A or B or C or D",
    "difficulty": "Easy or Medium or Hard",
    "explanation": "Short explanation in English"
  }}
]"""

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
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        text = res.json()["content"][0]["text"].strip()
        # Remove markdown if any
        text = text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(text)
        print(f"  ✅ {len(questions)} questions generated for {exam} - {subject}")
        return questions
    except Exception as e:
        print(f"  ⚠️ Claude error: {e}, using sample questions")
        key = f"{exam}_{subject}"
        return SAMPLE_QUESTIONS.get(key, SAMPLE_QUESTIONS["SSC_General Knowledge"])[:count]

def generate_all_quizzes():
    data = load_existing()
    next_id = max((q["id"] for q in data["quizzes"]), default=0) + 1

    for topic in TOPICS:
        exam = topic["exam"]
        subject = topic["subject"]
        key = f"{exam}_{subject}".replace(" ", "_")

        print(f"📝 Generating: {exam} — {subject}")
        questions = generate_with_claude(exam, subject, topic["count"])

        if not questions:
            continue

        # Quiz entry
        quiz = {
            "id": next_id,
            "exam": exam,
            "subject": subject,
            "subjectHi": topic["subjectHi"],
            "title": f"{exam} {subject} Practice",
            "titleHi": f"{exam} {topic['subjectHi']} अभ्यास",
            "questions": len(questions),
            "time": len(questions),
            "difficulty": "Mixed",
            "free": next_id % 3 != 0,  # Har 3rd quiz premium
            "addedDate": TODAY,
            "questionKey": key
        }

        # Check if quiz already exists
        existing_keys = [q.get("questionKey") for q in data["quizzes"]]
        if key in existing_keys:
            # Update existing questions
            data["questions"][key] = questions
            print(f"  🔄 Questions updated for {key}")
        else:
            data["quizzes"].append(quiz)
            data["questions"][key] = questions
            next_id += 1

    data["lastUpdated"] = TODAY
    return data

if __name__ == "__main__":
    print(f"📝 Quiz generation shuru — {TODAY}")
    data = generate_all_quizzes()
    save_data(data)
    total_q = sum(len(v) for v in data["questions"].values())
    print(f"✅ Done! {len(data['quizzes'])} quizzes, {total_q} total questions")

