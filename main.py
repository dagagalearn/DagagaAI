import requests
import time
import os
import random
import threading
from dotenv import load_dotenv
from flask import Flask

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

API_URL = f"https://api.telegram.org/bot{TOKEN}"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    f"models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
)

# ============================================================
# DAGAGA INFORMATION
# ============================================================

BIO_DATA = """
FULL NAME: Dagaga Addisu
NICKNAME NAME: Tesla
AGE: 18 (born Feb 29, 2008)
LOCATION: Ethiopia
OCCUPATION: Student
SCHOOL/UNIVERSITY: Wollega University Special Boarding Secondary School (WUSBSS)
INTERESTS: Coding, Learning Science, Solving Problems, Watching Movies
TECH STACK: HTML/CSS/JS, Python, TensorFlow, Basic ML tools
PERSONALITY: Protean and curious, witty, loves science and technology references
GOALS: No need to share here
FUN FACTS: Born on Leap day so uses Ethiopian Calendar to celebrate most birthdays
CONTACT: dagagaaddisulearn@gmail.com | dagagathecoder@gmail.com | @et_tesla
FAVORITES: IRON MAN, INTERSTELLAR, OPPENHEIMER
DAILY ROUTINE: Depends on the day and work that needs to be completed
WHAT YOU'RE LEARNING NOW: Currently taking two courses: AI and Calculus
GIRLFRIEND/MARRIAGE/RELATIONSHIP:
When asked about girlfriend/dating/relationships, respond with witty,
science/tech/movie-themed deflections. Never give serious answers.
EDUCATION LEVEL: High school | Grade 12
HOBBIES: Coding, learning something new, problem solving
PARENTS/FAMILY: 1 brother, 1 sister, father and mother (both teachers)
BLOOD TYPE: O-
BLOOD DONATION INFO:
Universal donor for red blood cells. Can donate to all blood types,
but can only receive O- red blood cells.
RELIGION: Protestant
LANGUAGES: Afan Oromo | Amharic | English
FAVORITE SUBJECT: Physics, Math and Informatics
"""

# ============================================================
# TELEGRAM
# ============================================================

def send_message(chat_id, text):
    try:
        url = f"{API_URL}/sendMessage"

        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=15
        )

        if not response.ok:
            print("TELEGRAM SEND ERROR:")
            print("Status:", response.status_code)
            print("Response:", response.text)

    except Exception as e:
        print("Telegram send exception:", repr(e))


def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"

    response = requests.get(
        url,
        params={
            "timeout": 30,
            "offset": offset
        },
        timeout=40
    )

    return response.json()


# ============================================================
# FALLBACK RESPONSES
# ============================================================

def get_creative_girlfriend_response():

    responses = [
        "Classified information - protected by a higher security clearance than Tony Stark's armor schematics.",
        "That data is encrypted with quantum cryptography. Even I can't access it.",
        "Some mysteries are better left unsolved, like what's inside a black hole or who Dagaga is dating.",
        "The only commitment Dagaga has right now is to his code and calculus homework.",
        "His current crushes are named Python, TensorFlow, and Calculus - and they're quite demanding.",
        "Dagaga's relationship status is like dark matter - we know it exists, but it's not directly observable.",
        "Dagaga's true love right now is solving complex problems and watching Interstellar.",
        "The only rings Dagaga is concerned with are in mathematics and planetary orbits.",
        "His primary partners are his IDE and textbook - they never complain about late-night debugging sessions.",
        "Error 404: Girlfriend not found. But you should see his GitHub repositories.",
        "Dagaga's dating life is like a leap year - it might exist, but it doesn't happen very often.",
        "Like Schrodinger's cat, Dagaga's relationship status is simultaneously all states until directly observed.",
        "He's in a committed relationship with the scientific method. It's complicated but rewarding.",
        "The only dates he's concerned with are deadlines and Ethiopian calendar dates.",
        "His love life is like a compressed file - you know something's there, but it's not easily accessible.",
        "He's following the Iron Man trajectory - genius first, love life later.",
        "His heart operates on a need-to-know basis, and right now, nobody needs to know."
    ]

    return random.choice(responses)


def get_fallback_response(question):

    question = question.lower().strip()

    # Relationship
    relationship_keywords = [
        "girlfriend", "boyfriend", "dating", "crush", "love",
        "single", "married", "wife", "husband", "partner",
        "relationship", "romantic", "romance", "valentine",
        "date", "heart", "couple"
    ]

    for keyword in relationship_keywords:
        if keyword in question:
            return get_creative_girlfriend_response()

    keyword_responses = {

        "email":
            "dagagaaddisulearn@gmail.com or dagagathecoder@gmail.com",

        "contact":
            "Email: dagagaaddisulearn@gmail.com\nTelegram: @et_tesla",

        "phone":
            "Telegram: @et_tesla\nEmail: dagagaaddisulearn@gmail.com",

        "telegram":
            "@et_tesla",

        "username":
            "@et_tesla on Telegram",

        "reach":
            "You can reach Dagaga at dagagaaddisulearn@gmail.com or @et_tesla",

        "nickname":
            "Tesla",

        "name":
            "Dagaga Addisu, also known as Tesla",

        "full name":
            "Dagaga Addisu",

        "who":
            "Dagaga Addisu, also known as Tesla. 18-year-old student from Ethiopia.",

        "age":
            "18 years old (Born February 29, 2008 - Leap Day!)",

        "birthday":
            "Born February 29, 2008 (Leap Day).",

        "born":
            "February 29, 2008 - Leap Day!",

        "school":
            "Wollega University Special Boarding Secondary School (WUSBSS)",

        "university":
            "Wollega University Special Boarding Secondary School (WUSBSS)",

        "study":
            "Wollega University Special Boarding Secondary School (WUSBSS)",

        "grade":
            "Grade 12 (High school)",

        "education":
            "High school, Grade 12 at Wollega University Special Boarding Secondary School",

        "student":
            "Yes, student at Wollega University Special Boarding Secondary School.",

        "occupation":
            "Student",

        "job":
            "Student",

        "movie":
            "Iron Man, Interstellar, Oppenheimer",

        "favorites":
            "Iron Man, Interstellar, Oppenheimer",

        "favorite":
            "Iron Man, Interstellar, Oppenheimer",

        "interest":
            "Coding, learning science, solving problems, watching movies",

        "hobby":
            "Coding, learning new things, problem solving",

        "hobbies":
            "Coding, learning new things, problem solving",

        "tech":
            "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",

        "stack":
            "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",

        "technology":
            "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",

        "programming":
            "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",

        "code":
            "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",

        "coding":
            "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",

        "learn":
            "Currently studying AI and Calculus",

        "learning":
            "Currently studying AI and Calculus",

        "course":
            "Currently taking two courses: AI and Calculus",

        "studying":
            "Currently taking two courses: AI and Calculus",

        "subject":
            "Physics, Math, and Informatics are favorite subjects",

        "physics":
            "Physics is one of his favorite subjects",

        "math":
            "Math is one of his favorite subjects",

        "informatics":
            "Informatics is one of his favorite subjects",

        "language":
            "Afan Oromo, Amharic, English",

        "speak":
            "Afan Oromo, Amharic, English",

        "oromo":
            "Yes, he speaks Afan Oromo",

        "amharic":
            "Yes, he speaks Amharic",

        "english":
            "Yes, he speaks English",

        "location":
            "Ethiopia",

        "where":
            "Ethiopia",

        "country":
            "Ethiopia",

        "ethiopia":
            "Yes, Dagaga is from Ethiopia",

        "family":
            "1 brother, 1 sister, father and mother (both are teachers)",

        "parent":
            "Both parents are teachers",

        "father":
            "Father is a teacher",

        "mother":
            "Mother is a teacher",

        "sibling":
            "1 brother and 1 sister",

        "brother":
            "Has 1 brother",

        "sister":
            "Has 1 sister",

        "blood type":
            "Blood type: O-",

        "blood":
            "Blood type: O-",

        "donation":
            "O- is the universal red-blood-cell donor type.",

        "donate":
            "O- can donate red blood cells to all blood types.",

        "receive blood":
            "A person with O- blood can receive O- red blood cells.",

        "transfusion":
            "Blood type: O-",

        "universal donor":
            "O- is the universal red-blood-cell donor type.",

        "o negative":
            "Blood type: O-",

        "religion":
            "Protestant",

        "personality":
            "Protean and curious - adaptable and always learning",

        "fact":
            "Born on Leap Day (February 29, 2008)!",

        "fun fact":
            "Born on Leap Day (February 29, 2008)!"
    }

    # Exact/keyword matching
    for keyword, response in keyword_responses.items():
        if keyword in question:
            return response

    return (
        "I don't have that information in my offline database. "
        "You can ask Dagaga directly at @et_tesla."
    )


# ============================================================
# GEMINI AI
# ============================================================

def ask_rag(question):

    if not GEMINI_API_KEY:
        print("=" * 60)
        print("GEMINI ERROR: GOOGLE_API_KEY IS MISSING")
        print("Set GOOGLE_API_KEY in your Render environment variables.")
        print("=" * 60)
        return None

    prompt = f"""
You are Dagaga's personal AI assistant.

Answer questions about Dagaga using ONLY the information provided below.

RULES:
1. Answer in 2-4 complete sentences.
2. Never invent information.
3. If the information is unavailable, say:
   "I don't know. Ask him @et_tesla on Telegram!"
4. For relationship questions, use witty science/technology/movie-themed deflections.
5. Be concise.
6. Complete every sentence.

INFORMATION ABOUT DAGAGA:
{BIO_DATA}

QUESTION:
{question}

ANSWER:
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

    for attempt in range(3):

        try:

            print("=" * 60)
            print(f"GEMINI API ATTEMPT {attempt + 1}/3")
            print("Question:", question)
            print("API key exists:", bool(GEMINI_API_KEY))
            print("API key length:", len(GEMINI_API_KEY))
            print("Sending request...")
            print("=" * 60)

            response = requests.post(
                GEMINI_URL,
                json=payload,
                timeout=30
            )

            print("=" * 60)
            print("GEMINI HTTP STATUS:", response.status_code)
            print("GEMINI RAW RESPONSE:")
            print(response.text)
            print("=" * 60)

            # HTTP failure
            if not response.ok:

                try:
                    result = response.json()
                    error = result.get("error", {})

                    print("GEMINI ERROR CODE:", error.get("code"))
                    print("GEMINI ERROR STATUS:", error.get("status"))
                    print("GEMINI ERROR MESSAGE:", error.get("message"))

                except Exception:
                    print("Could not parse Gemini error as JSON.")

                # Retry rate-limit/server errors
                if response.status_code in [429, 500, 502, 503, 504]:
                    wait = (attempt + 1) * 3
                    print(f"Retrying in {wait} seconds...")
                    time.sleep(wait)
                    continue

                return None

            result = response.json()

            # Check candidates
            if "candidates" not in result:

                print("GEMINI ERROR: No candidates in response.")
                print("Full response:", result)

                return None

            candidates = result["candidates"]

            if not candidates:
                print("GEMINI ERROR: Empty candidates list.")
                return None

            candidate = candidates[0]

            # Check finish reason
            print("Finish reason:", candidate.get("finishReason"))

            content = candidate.get("content")

            if not content:
                print("GEMINI ERROR: No content in candidate.")
                return None

            parts = content.get("parts", [])

            if not parts:
                print("GEMINI ERROR: No parts in content.")
                return None

            answer = parts[0].get("text")

            if not answer:
                print("GEMINI ERROR: No text in response.")
                return None

            print("GEMINI SUCCESS")
            print("Answer:", answer)

            return answer.strip()

        except requests.exceptions.Timeout:
            print("GEMINI ERROR: Request timed out.")

        except requests.exceptions.ConnectionError as e:
            print("GEMINI ERROR: Connection error.")
            print(repr(e))

        except Exception as e:
            print("GEMINI UNEXPECTED ERROR:")
            print(type(e).__name__, str(e))

        if attempt < 2:
            print("Retrying in 3 seconds...")
            time.sleep(3)

    print("=" * 60)
    print("GEMINI FAILED AFTER 3 ATTEMPTS")
    print("=" * 60)

    return None


# ============================================================
# FLASK SERVER
# ============================================================

@app.route("/")
def home():
    return "Dagaga Telegram AI Bot is running."


@app.route("/health")
def health():
    return {
        "status": "running",
        "telegram_key": bool(TOKEN),
        "gemini_key": bool(GEMINI_API_KEY)
    }


def run_flask():

    port = int(os.environ.get("PORT", 10000))

    print(f"Starting Flask server on port {port}")

    app.run(
        host="0.0.0.0",
        port=port
    )


# ============================================================
# MAIN TELEGRAM LOOP
# ============================================================

def main():

    print("=" * 60)
    print("STARTING DAGAGA AI TELEGRAM BOT")
    print("=" * 60)

    # Check environment variables
    print("TELEGRAM_BOT_TOKEN exists:", bool(TOKEN))
    print("GOOGLE_API_KEY exists:", bool(GEMINI_API_KEY))

    if GEMINI_API_KEY:
        print("Gemini API key length:", len(GEMINI_API_KEY))

    # Telegram connection test
    try:

        test = requests.get(
            f"{API_URL}/getMe",
            timeout=15
        )

        print("Telegram HTTP status:", test.status_code)
        print("Telegram response:", test.text)

        data = test.json()

        if not data.get("ok"):
            print("INVALID TELEGRAM TOKEN")
            return

        print(
            f"Telegram bot: @{data['result']['username']}"
        )

    except Exception as e:

        print("TELEGRAM CONNECTION ERROR:")
        print(repr(e))
        return

    # Gemini configuration check
    if not GEMINI_API_KEY:

        print("=" * 60)
        print("WARNING: GOOGLE_API_KEY IS NOT SET")
        print("AI WILL NOT WORK.")
        print("Add GOOGLE_API_KEY to Render Environment Variables.")
        print("=" * 60)

    print("Bot is ready.")
    print("Waiting for Telegram messages...")

    offset = None

    while True:

        try:

            updates = get_updates(offset)

            if not updates.get("ok"):

                print("Telegram getUpdates failed:")
                print(updates)

                time.sleep(5)
                continue

            if updates.get("result"):

                for update in updates["result"]:

                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]

                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")
                    user = msg.get("from", {}).get(
                        "first_name",
                        "User"
                    )

                    print("=" * 60)
                    print("NEW MESSAGE")
                    print("User:", user)
                    print("Message:", text)
                    print("=" * 60)

                    # /start
                    if text == "/start":

                        reply = (
                            "Hi! I'm Dagaga's AI assistant.\n"
                            "Ask me anything about Dagaga!\n\n"
                            "Examples:\n"
                            "- What's his email?\n"
                            "- Where does he study?\n"
                            "- What's his tech stack?\n"
                            "- What grade is he in?\n"
                            "- Favorite movies?\n"
                            "- What languages does he speak?\n"
                            "- Tell me about his hobbies"
                        )

                        send_message(chat_id, reply)

                        continue

                    # ==================================================
                    # AI REQUEST
                    # ==================================================

                    api_response = ask_rag(text)

                    if api_response:

                        send_message(
                            chat_id,
                            api_response
                        )

                        print("AI RESPONSE SENT")

                    else:

                        print("AI FAILED -> USING OFFLINE DATABASE")

                        reply = (
                            "AI service is currently unavailable.\n\n"
                            + get_fallback_response(text)
                            + "\n\n"
                            "Check the Render logs for the exact Gemini error."
                        )

                        send_message(
                            chat_id,
                            reply
                        )

                        print("OFFLINE RESPONSE SENT")

            time.sleep(1)

        except Exception as e:

            print("=" * 60)
            print("MAIN LOOP ERROR")
            print(type(e).__name__, str(e))
            print("=" * 60)

            time.sleep(5)


# ============================================================
# START EVERYTHING
# ============================================================

if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    main()