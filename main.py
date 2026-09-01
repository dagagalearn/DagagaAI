import requests
import time
import os
import random
import threading
from dotenv import load_dotenv
from flask import Flask

print("========== PROGRAM STARTING ==========", flush=True)

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

print("TELEGRAM TOKEN EXISTS:", bool(TOKEN), flush=True)
print("GOOGLE API KEY EXISTS:", bool(GEMINI_API_KEY), flush=True)

API_URL = f"https://api.telegram.org/bot{TOKEN}"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
)


# ============================================================
# FLASK
# ============================================================

@app.route("/")
def home():
    return "Bot is running."


@app.route("/health")
def health():
    return {
        "status": "running",
        "telegram_token": bool(TOKEN),
        "gemini_key": bool(GEMINI_API_KEY)
    }


def run_flask():
    port = int(os.environ.get("PORT", 10000))

    print(
        f"========== FLASK STARTING ON PORT {port} ==========",
        flush=True
    )

    app.run(
        host="0.0.0.0",
        port=port
    )


# ============================================================
# TELEGRAM
# ============================================================

def send_message(chat_id, text):

    try:

        response = requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=15
        )

        print(
            "Telegram send status:",
            response.status_code,
            flush=True
        )

        if not response.ok:
            print(
                "Telegram error:",
                response.text,
                flush=True
            )

    except Exception as e:

        print(
            "Telegram SEND ERROR:",
            repr(e),
            flush=True
        )


def get_updates(offset=None):

    response = requests.get(
        f"{API_URL}/getUpdates",
        params={
            "timeout": 30,
            "offset": offset
        },
        timeout=40
    )

    return response.json()


# ============================================================
# OFFLINE DATABASE
# ============================================================

def get_fallback_response(question):

    q = question.lower().strip()

    if "girlfriend" in q or "dating" in q or "relationship" in q:
        return random.choice([
            "Error 404: Girlfriend not found.",
            "That information is classified.",
            "His relationship status is like dark matter: theoretically interesting, experimentally unavailable.",
            "The only relationship currently receiving significant CPU time is with Python and calculus."
        ])

    responses = {

        "email":
            "dagagaaddisulearn@gmail.com or dagagathecoder@gmail.com",

        "telegram":
            "@et_tesla",

        "username":
            "@et_tesla",

        "name":
            "Dagaga Addisu, also known as Tesla.",

        "age":
            "18 years old.",

        "school":
            "Wollega University Special Boarding Secondary School (WUSBSS).",

        "university":
            "Wollega University Special Boarding Secondary School (WUSBSS).",

        "grade":
            "Grade 12.",

        "movie":
            "Iron Man, Interstellar, and Oppenheimer.",

        "favorite":
            "Iron Man, Interstellar, and Oppenheimer.",

        "tech":
            "Python, HTML/CSS/JS, TensorFlow, and basic ML tools.",

        "coding":
            "Python, HTML/CSS/JS, TensorFlow, and basic ML tools.",

        "learning":
            "Currently studying AI and Calculus.",

        "physics":
            "Physics is one of his favorite subjects.",

        "math":
            "Math is one of his favorite subjects.",

        "language":
            "Afan Oromo, Amharic, and English.",

        "oromo":
            "Yes, he speaks Afan Oromo.",

        "amharic":
            "Yes, he speaks Amharic.",

        "english":
            "Yes, he speaks English.",

        "location":
            "Ethiopia.",

        "family":
            "1 brother, 1 sister, father and mother.",

        "blood":
            "Blood type O-.",

        "hobby":
            "Coding, learning new things, and problem solving."
    }

    for keyword, answer in responses.items():

        if keyword in q:
            return answer

    return (
        "I don't have that information in my offline database. "
        "Ask Dagaga directly at @et_tesla."
    )


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(question):

    print("========== GEMINI FUNCTION CALLED ==========", flush=True)

    if not GEMINI_API_KEY:

        print(
            "GEMINI ERROR: GOOGLE_API_KEY DOES NOT EXIST",
            flush=True
        )

        return None

    prompt = f"""
You are Dagaga's personal AI assistant.

Use ONLY the information below.

BIO DATA:
{BIO_DATA}

QUESTION:
{question}

Give a concise answer.
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 500
        }
    }

    try:

        print("Sending request to Gemini...", flush=True)

        response = requests.post(
            GEMINI_URL,
            json=payload,
            timeout=30
        )

        print(
            "GEMINI STATUS:",
            response.status_code,
            flush=True
        )

        print(
            "GEMINI RESPONSE:",
            response.text,
            flush=True
        )

        if not response.ok:
            return None

        data = response.json()

        return (
            data["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

    except Exception as e:

        print(
            "========== GEMINI EXCEPTION ==========",
            flush=True
        )

        print(
            type(e).__name__,
            str(e),
            flush=True
        )

        return None


# ============================================================
# BIO DATA
# ============================================================

BIO_DATA = """
FULL NAME: Dagaga Addisu
NICKNAME: Tesla
AGE: 18
LOCATION: Ethiopia
OCCUPATION: Student
SCHOOL: Wollega University Special Boarding Secondary School
INTERESTS: Coding, science, problem solving, movies
TECH STACK: HTML/CSS/JS, Python, TensorFlow, basic ML
CURRENTLY LEARNING: AI and Calculus
FAVORITE MOVIES: Iron Man, Interstellar, Oppenheimer
LANGUAGES: Afan Oromo, Amharic, English
FAVORITE SUBJECTS: Physics, Math, Informatics
"""


# ============================================================
# MAIN BOT
# ============================================================

def main():

    print("========== MAIN() STARTED ==========", flush=True)

    if not TOKEN:

        print(
            "FATAL ERROR: TELEGRAM_BOT_TOKEN IS MISSING",
            flush=True
        )

        return

    try:

        print(
            "Testing Telegram connection...",
            flush=True
        )

        test = requests.get(
            f"{API_URL}/getMe",
            timeout=15
        )

        print(
            "Telegram status:",
            test.status_code,
            flush=True
        )

        print(
            "Telegram response:",
            test.text,
            flush=True
        )

        data = test.json()

        if not data.get("ok"):

            print(
                "FATAL: TELEGRAM TOKEN INVALID",
                flush=True
            )

            return

        print(
            "BOT:",
            data["result"]["username"],
            flush=True
        )

    except Exception as e:

        print(
            "TELEGRAM CONNECTION ERROR:",
            repr(e),
            flush=True
        )

        return

    print(
        "========== BOT READY ==========",
        flush=True
    )

    offset = None

    while True:

        try:

            updates = get_updates(offset)

            if not updates.get("ok"):

                print(
                    "getUpdates ERROR:",
                    updates,
                    flush=True
                )

                time.sleep(5)
                continue

            for update in updates.get("result", []):

                offset = update["update_id"] + 1

                if "message" not in update:
                    continue

                message = update["message"]

                chat_id = message["chat"]["id"]

                text = message.get("text", "")

                print(
                    "========== NEW MESSAGE ==========",
                    flush=True
                )

                print(
                    "Message:",
                    text,
                    flush=True
                )

                if text == "/start":

                    send_message(
                        chat_id,
                        "Hi! I'm Dagaga's AI assistant. Ask me anything about Dagaga."
                    )

                    continue

                # AI FIRST
                ai_response = ask_gemini(text)

                if ai_response:

                    print(
                        "AI RESPONSE SUCCESS",
                        flush=True
                    )

                    send_message(
                        chat_id,
                        ai_response
                    )

                else:

                    print(
                        "AI FAILED -> USING OFFLINE DATABASE",
                        flush=True
                    )

                    send_message(
                        chat_id,
                        get_fallback_response(text)
                    )

        except Exception as e:

            print(
                "========== MAIN LOOP ERROR ==========",
                flush=True
            )

            print(
                type(e).__name__,
                str(e),
                flush=True
            )

            time.sleep(5)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print(
        "========== STARTING SERVERS ==========",
        flush=True
    )

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    main()