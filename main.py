import requests
import time
import os
import random
from dotenv import load_dotenv
import threading
from flask import Flask

# Create a dummy web server to satisfy Render's HTTP health check





load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_API_KEY}"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

BIO_DATA = """
FULL NAME: Dagaga Addisu
NICKNAME NAME: Tesla
AGE: 18(born Feb 29,2008)
LOCATION: Ethiopia
OCCUPATION: Student
SCHOOL/UNIVERSITY: Wollega University Special Boarding Secondary School(a.k.a WUSBSS)
INTERESTS: Coding, Learning Science, Solving Problems, Watching Movies
TECH STACK: HTML/CSS/JS, Python, tensorflow,Basic ML tools
PERSONALITY: Protean and curious, witty, loves science and technology references
GOALS: No need to share here
FUN FACTS: Born on Leap day so uses Ethiopian Calendar to celebrate most birthdays
CONTACT: dagagaaddisulearn@gmail.com | dagagathecoder@gmail.com | @et_tesla (telegram)
FAVORITES: IRON MAN, INTERSTELLAR, OPPENHEIMER
DAILY ROUTINE: depends on the day and works that need to be completed(variable)
WHAT YOU'RE LEARNING NOW: Currently taking two courses: AI and Calculus
GIRLFRIEND/MARRIAGE/RELATIONSHIP: When asked about girlfriend/dating/relationships, respond with witty, science/tech/movie-themed deflections. Never give serious answers to these questions.
EDUCATION LEVEL: highschool | Grade 12
HOBBIES: coding, learning something(and someone) new, problem solving etc.
PARENTS/FAMILY: 1 brother, 1 sister, father and mother(both are teachers)
BLOOD TYPE: O-
BLOOD DONATION INFO: Universal donor (O-). Can donate to all blood types. Can only receive O- blood.
RELIGION: protestant
LANGUAGES: Afan Oromo | Amharic | English
FAVORITE SUBJECT: Physics, Math and Informatics
"""

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def get_updates(offset=None):
    url = f"{API_URL}/getUpdates"
    response = requests.get(url, params={"timeout": 30, "offset": offset})
    return response.json()

def get_creative_girlfriend_response():
    """Return random witty response about relationship status"""
    responses = [
        "Classified information - protected by a higher security clearance than Tony Stark's armor schematics.",
        "That data is encrypted with quantum cryptography. Even I can't access it.",
        "Some mysteries are better left unsolved, like what's inside a black hole or who Dagaga is dating.",
        "The only commitment Dagaga has right now is to his code and calculus homework.",
        "His current crushes are named Python, TensorFlow, and Calculus - and they're quite demanding.",
        "Dagaga's relationship status is like dark matter - we know it exists, but it's not directly observable.",
        "Dagaga's true love right now is solving complex problems and watching Interstellar for the 100th time.",
        "The only rings Dagaga is concerned with are in mathematics and planetary orbits.",
        "His primary partners are his IDE and textbook - they never complain about late-night debugging sessions.",
        "Error 404: Girlfriend not found. But you should see his GitHub repositories - they're beautiful.",
        "Dagaga's heart is like his blood type: O- (Zero negativity, zero drama, zero public information).",
        "His dating life is like a leap year - it might exist, but it's not happening on February 29th anytime soon.",
        "Like Schrodinger's cat, Dagaga's relationship status is simultaneously all states until directly observed.",
        "He's in a committed relationship with the scientific method. It's complicated but rewarding.",
        "The only dates he's concerned with are deadlines and Ethiopian calendar dates.",
        "Dagaga's love life is like a compressed file - you know something's there, but it's not easily accessible.",
        "He's following the Iron Man trajectory - genius first, love life later. Pepper Potts can wait.",
        "His heart operates on a need-to-know basis, and right now, nobody needs to know."
    ]
    return random.choice(responses)

def get_fallback_response(question):
    """Enhanced offline response logic with keyword matching and context awareness"""
    question = question.lower().strip()
    
    # Creative girlfriend/relationship responses (checked first)
    relationship_keywords = ["girlfriend", "boyfriend", "dating", "crush", "love", "single", 
                            "married", "wife", "husband", "partner", "relationship", "romantic",
                            "romance", "valentine", "date", "heart", "couple"]
    for keyword in relationship_keywords:
        if keyword in question:
            return get_creative_girlfriend_response()
    
    # Direct keyword matches for common questions
    keyword_responses = {
        # Contact Info
        "email": "dagagaaddisulearn@gmail.com or dagagathecoder@gmail.com",
        "contact": "Email: dagagaaddisulearn@gmail.com\nTelegram: @et_tesla",
        "phone": "Telegram: @et_tesla\nEmail: dagagaaddisulearn@gmail.com",
        "telegram": "@et_tesla",
        "username": "@et_tesla on Telegram",
        "reach": "You can reach Dagaga at dagagaaddisulearn@gmail.com or @et_tesla on Telegram",
        
        # Identity
        "nickname": "Tesla (also known as Nikola Tesla)",
        "name": "Dagaga Addisu, also known as Tesla",
        "full name": "Dagaga Addisu",
        "who": "Dagaga Addisu, also known as Tesla. 18-year-old student from Ethiopia.",
        "what": "Dagaga Addisu - student, coder, and curious learner",
        
        # Age & Birthday
        "age": "18 years old (Born February 29, 2008 - Leap Day!)",
        "birthday": "Born on February 29, 2008 (Leap Day). Uses Ethiopian Calendar for most birthday celebrations",
        "born": "February 29, 2008 - Leap Day!",
        "old": "18 years old (Born February 29, 2008 - Leap Day!)",
        
        # Education
        "school": "Wollega University Special Boarding Secondary School (WUSBSS)",
        "university": "Wollega University Special Boarding Secondary School (WUSBSS)",
        "study": "Wollega University Special Boarding Secondary School (WUSBSS)",
        "grade": "Grade 12 (High school)",
        "education": "High school, Grade 12 at Wollega University Special Boarding Secondary School",
        "level": "Grade 12 (High school)",
        "highschool": "Grade 12 at Wollega University Special Boarding Secondary School (WUSBSS)",
        "student": "Yes, student at Wollega University Special Boarding Secondary School (Grade 12)",
        "occupation": "Student at Wollega University Special Boarding Secondary School",
        "job": "Student",
        
        # Interests & Hobbies
        "movie": "Iron Man, Interstellar, Oppenheimer",
        "favorites": "Iron Man, Interstellar, Oppenheimer",
        "favorite": "Iron Man, Interstellar, Oppenheimer",
        "interest": "Coding, Learning Science, Solving Problems, Watching Movies",
        "hobby": "Coding, learning new things, problem solving",
        "hobbies": "Coding, learning new things, problem solving",
        
        # Tech Stack
        "tech": "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",
        "stack": "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",
        "technology": "HTML/CSS/JS, Python, TensorFlow, Basic ML tools",
        "programming": "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",
        "code": "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",
        "coding": "Python, HTML/CSS/JS, TensorFlow, Basic ML tools",
        
        # Learning
        "learn": "Currently studying AI and Calculus",
        "learning": "Currently studying AI and Calculus",
        "course": "Currently taking two courses: AI and Calculus",
        "studying": "Currently taking two courses: AI and Calculus",
        
        # Subjects
        "subject": "Physics, Math, and Informatics are favorite subjects",
        "favorite subject": "Physics, Math, and Informatics",
        "physics": "Physics is one of his favorite subjects",
        "math": "Math is one of his favorite subjects",
        "informatics": "Informatics is one of his favorite subjects",
        
        # Languages
        "language": "Afan Oromo, Amharic, English",
        "speak": "Afan Oromo, Amharic, English",
        "oromo": "Yes, he speaks Afan Oromo",
        "amharic": "Yes, he speaks Amharic",
        "english": "Yes, he speaks English",
        
        # Location
        "location": "Ethiopia",
        "where": "Ethiopia",
        "country": "Ethiopia",
        "ethiopia": "Yes, Dagaga is from Ethiopia",
        
        # Family
        "family": "1 brother, 1 sister, father and mother (both are teachers)",
        "parent": "Both parents are teachers",
        "father": "Father is a teacher",
        "mother": "Mother is a teacher",
        "sibling": "1 brother and 1 sister",
        "brother": "Has 1 brother",
        "sister": "Has 1 sister",
        
        # Blood
        "blood": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "blood type": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "donation": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "donate": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "receive blood": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "transfusion": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        "universal donor": "Yes! Blood type O- makes Dagaga a universal donor. He can donate to anyone but can only receive O- blood.",
        "o negative": "Blood type: O- (Universal donor). Can donate to all blood types but can only receive O- blood.",
        
        # Other
        "religion": "Protestant",
        "personality": "Protean and curious - adaptable and always learning",
        "goal": "Information about Dagaga's goals is not available",
        "fact": "Born on Leap Day (February 29, 2008)! Uses Ethiopian Calendar to celebrate most birthdays",
        "fun fact": "Born on Leap Day (February 29, 2008)! Uses Ethiopian Calendar to celebrate most birthdays",
        "routine": "Daily routine varies depending on the day and tasks that need to be completed",
        "daily": "Daily routine varies depending on the day and tasks that need to be completed",
        "schedule": "Daily routine varies depending on the day and tasks that need to be completed",
        
        # Help
        "tell me": "I know about Dagaga Addisu (Tesla). Ask me something specific like email, school, age, tech stack, interests, blood type, etc.",
        "help": "I can tell you about Dagaga's email, school, age, tech stack, interests, favorites, family, languages, blood type, and more. Just ask!",
        "info": "I can tell you about Dagaga's email, school, age, tech stack, interests, favorites, family, languages, blood type, and more. Just ask!"
    }
    
    # Check for exact keyword matches first
    for keyword, response in keyword_responses.items():
        if keyword in question:
            return response
    
    # Context-based matching for multi-word queries
    if "what is" in question or "what's" in question or "tell" in question:
        words = question.replace("what is", "").replace("what's", "").replace("tell me about", "").replace("tell me", "").replace("tell about", "").strip()
        for keyword, response in keyword_responses.items():
            if keyword in words:
                return response
    
    # If question contains "about" and some context
    if "about" in question:
        context = question.split("about")[-1].strip()
        for keyword, response in keyword_responses.items():
            if keyword in context:
                return response
    
    # If question contains "does he" or "is he" type questions
    if "does he" in question or "is he" in question or "can he" in question:
        for keyword, response in keyword_responses.items():
            if keyword in question:
                return response
    
    return "I don't have that information in my offline database. You can ask Dagaga directly at @et_tesla on Telegram or email dagagaaddisulearn@gmail.com"

def ask_rag(question):
    """Try Gemini API with retries, fallback if fails"""
    prompt = f"""You are Dagaga's personal assistant with a witty personality that loves science and technology.
Answer questions about Dagaga using ONLY the information below.

CRITICAL INSTRUCTIONS:
1. Complete EVERY sentence fully. Never cut off mid-thought or mid-sentence.
2. If you start a joke, metaphor, or comparison, ALWAYS finish it completely.
3. Keep responses to 2-4 complete sentences maximum.
4. End with proper punctuation (period, exclamation mark, question mark).
5. For relationship/girlfriend/dating questions: Give creative, witty, science/tech/movie-themed deflections. Complete the joke fully.
6. For blood donation questions: Clearly explain O- universal donor status.
7. If information is not available: Say "I don't know. Ask him @et_tesla on Telegram!"

INFORMATION ABOUT DAGAGA:
{BIO_DATA}

QUESTION: {question}

COMPLETE ANSWER (finish all sentences):"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500,
            "topP": 0.95,
            "topK": 40
        }
    }

    for attempt in range(3):
        try:
            print(f"API attempt {attempt + 1}/3...")
            response = requests.post(GEMINI_URL, json=payload, timeout=15)
            result = response.json()
            
            if "candidates" in result:
                answer = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Check if response seems cut off
                if answer and not answer.rstrip().endswith(('.', '!', '?', '"', ')', ']')):
                    print("Warning: Response may be incomplete, but using anyway...")
                
                print("API success")
                return answer
                
            elif "error" in result:
                error_msg = result["error"]["message"]
                if "high demand" in error_msg.lower() or "overloaded" in error_msg.lower():
                    wait = (attempt + 1) * 3
                    print(f"High demand, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"API Error: {error_msg}")
                    break
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")
            if attempt < 2:
                time.sleep(3)
    
    return None

def main():
    print("Bot starting...")
    
    # Verify connection
    test = requests.get(f"{API_URL}/getMe")
    if test.json().get("ok"):
        print(f"Bot: @{test.json()['result']['username']}")
    else:
        print("Invalid token!")
        return
    
    print("Ready! Send /start on Telegram")
    
    # Track API status
    api_failed = False
    last_api_attempt = 0
    
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        user = msg.get("from", {}).get("first_name", "User")
                        
                        print(f"Message from {user}: {text}")
                        
                        if text == "/start":
                            reply = (
                                "Hi! I'm Dagaga's AI assistant.\n"
                                "Ask me anything about Dagaga!\n\n"
                                "Examples:\n"
                                "- What's his email?\n"
                                "- Where does he study?\n"
                                "- Tech stack?\n"
                                "- Grade level?\n"
                                "- Favorite movies?\n"
                                "- Languages he speaks?\n"
                                "- Family?\n"
                                "- Blood type?\n"
                                "- What blood can he donate/receive?\n"
                                "- Tell me about his hobbies"
                            )
                            send_message(chat_id, reply)
                            print("Sent welcome message")
                            continue
                        
                        # Try API first
                        current_time = time.time()
                        if api_failed and current_time - last_api_attempt < 60:
                            # API recently failed, use offline mode with notification
                            reply = "Note: I'm currently in offline mode as the AI service is temporarily unavailable. Responses will come from my local database.\n\n"
                            reply += get_fallback_response(text)
                            send_message(chat_id, reply)
                            print("Sent offline response")
                        else:
                            # Try API
                            api_response = ask_rag(text)
                            
                            if api_response:
                                # API worked
                                api_failed = False
                                send_message(chat_id, api_response)
                                print("Sent API response")
                            else:
                                # API failed
                                api_failed = True
                                last_api_attempt = current_time
                                reply = "The AI service is temporarily unavailable due to high demand or connectivity issues. I'm switching to offline mode. You'll still get accurate answers from my database.\n\n"
                                reply += get_fallback_response(text)
                                reply += "\n\nNote: These responses are from pre-loaded information and may be more limited. You can try again later for AI-powered responses."
                                send_message(chat_id, reply)
                                print("Sent offline fallback response")
            
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Run Flask web server in a background thread
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    # Run your original Telegram polling main function
    main()
