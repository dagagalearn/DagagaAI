import requests
import time
import os
import random
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from functools import lru_cache

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
@dataclass
class Config:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GEMINI_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Updated model name
    API_BASE_URL: str = "https://api.telegram.org/bot"
    GEMINI_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 3
    OFFLINE_COOLDOWN: int = 60  # seconds

config = Config()
API_URL = f"{config.API_BASE_URL}{config.TELEGRAM_TOKEN}"
GEMINI_URL = f"{config.GEMINI_URL}/{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"

BIO_DATA = """
FULL NAME: Dagaga Addisu
NICKNAME NAME: Tesla
AGE: 18 (born Feb 29, 2008)
LOCATION: Ethiopia
OCCUPATION: Student
SCHOOL/UNIVERSITY: Wollega University Special Boarding Secondary School (a.k.a WUSBSS)
INTERESTS: Coding, Learning Science, Solving Problems, Watching Movies
TECH STACK: HTML/CSS/JS, Python, TensorFlow, Basic ML tools
PERSONALITY: Protean and curious, witty, loves science and technology references
GOALS: No need to share here
FUN FACTS: Born on Leap day, uses Ethiopian Calendar to celebrate most birthdays
CONTACT: dagagaaddisulearn@gmail.com | dagagathecoder@gmail.com | @et_tesla (telegram)
FAVORITES: IRON MAN, INTERSTELLAR, OPPENHEIMER
DAILY ROUTINE: Variable depending on day and tasks
WHAT YOU'RE LEARNING NOW: Currently taking AI and Calculus courses
GIRLFRIEND/MARRIAGE/RELATIONSHIP: When asked about girlfriend/dating/relationships, respond with witty, science/tech/movie-themed deflections
EDUCATION LEVEL: High school, Grade 12
HOBBIES: Coding, learning new things, problem solving
PARENTS/FAMILY: 1 brother, 1 sister, father and mother (both teachers)
BLOOD TYPE: O-
BLOOD DONATION INFO: Universal donor (O-). Can donate to all blood types. Can only receive O- blood.
RELIGION: Protestant
LANGUAGES: Afan Oromo, Amharic, English
FAVORITE SUBJECT: Physics, Math, Informatics
"""

class TelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.api_failed = False
        self.last_api_attempt = 0
        self.relationship_responses = self._load_relationship_responses()
        self.keyword_responses = self._load_keyword_responses()
        
    def _load_relationship_responses(self) -> list:
        """Load witty relationship responses"""
        return [
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
    
    def _load_keyword_responses(self) -> Dict[str, str]:
        """Load keyword-based responses"""
        return {
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
    
    def send_message(self, chat_id: int, text: str) -> bool:
        """Send message to Telegram chat"""
        try:
            url = f"{API_URL}/sendMessage"
            response = self.session.post(
                url, 
                json={"chat_id": chat_id, "text": text},
                timeout=10
            )
            return response.json().get("ok", False)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def get_updates(self, offset: Optional[int] = None) -> Dict[str, Any]:
        """Get updates from Telegram"""
        try:
            url = f"{API_URL}/getUpdates"
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            response = self.session.get(url, params=params, timeout=35)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return {"ok": False, "result": []}
    
    def get_creative_girlfriend_response(self) -> str:
        """Return random witty response about relationship status"""
        return random.choice(self.relationship_responses)
    
    def get_fallback_response(self, question: str) -> str:
        """Enhanced offline response logic with keyword matching"""
        question = question.lower().strip()
        
        # Check relationship keywords first
        relationship_keywords = [
            "girlfriend", "boyfriend", "dating", "crush", "love", "single",
            "married", "wife", "husband", "partner", "relationship", "romantic",
            "romance", "valentine", "date", "heart", "couple"
        ]
        
        if any(keyword in question for keyword in relationship_keywords):
            return self.get_creative_girlfriend_response()
        
        # Direct keyword matches
        for keyword, response in self.keyword_responses.items():
            if keyword in question:
                return response
        
        # Context-based matching
        question_words = set(question.replace("?", "").replace("what", "").replace("is", "").split())
        for keyword in self.keyword_responses:
            if keyword in question_words:
                return self.keyword_responses[keyword]
        
        return "I don't have that information in my offline database. You can ask Dagaga directly at @et_tesla on Telegram or email dagagaaddisulearn@gmail.com"
    
    def ask_rag(self, question: str) -> Optional[str]:
        """Try Gemini API with retries"""
        prompt = f"""You are Dagaga's personal assistant with a witty personality that loves science and technology.
Answer questions about Dagaga using ONLY the information below.

CRITICAL INSTRUCTIONS:
1. Complete EVERY sentence fully. Never cut off mid-thought or mid-sentence.
2. If you start a joke, metaphor, or comparison, ALWAYS finish it completely.
3. Keep responses to 2-4 complete sentences maximum.
4. End with proper punctuation (period, exclamation mark, question mark).
5. For relationship/girlfriend/dating questions: Give creative, witty, science/tech/movie-themed deflections.
6. For blood donation questions: Clearly explain O- universal donor status.
7. If information is not available: Say "I don't know. Ask him @et_tesla on Telegram!"

INFORMATION ABOUT DAGAGA:
{BIO_DATA}

QUESTION: {question}

COMPLETE ANSWER (finish all sentences):"""
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 150
            }
        }
        
        for attempt in range(self.config.MAX_RETRIES):
            try:
                logger.info(f"API attempt {attempt + 1}/{self.config.MAX_RETRIES}")
                response = self.session.post(
                    GEMINI_URL, 
                    json=payload, 
                    timeout=15
                )
                result = response.json()
                
                if "candidates" in result:
                    answer = result["candidates"][0]["content"]["parts"][0]["text"]
                    return answer.strip()
                
                elif "error" in result:
                    error_msg = result["error"].get("message", "Unknown error")
                    logger.warning(f"API error: {error_msg}")
                    
                    if "high demand" in error_msg.lower() or "overloaded" in error_msg.lower():
                        wait_time = (attempt + 1) * self.config.RETRY_DELAY
                        logger.info(f"Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        break
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {e}")
                if attempt < self.config.MAX_RETRIES - 1:
                    time.sleep(self.config.RETRY_DELAY)
        
        return None
    
    def handle_message(self, chat_id: int, text: str, user_name: str) -> None:
        """Handle incoming message"""
        logger.info(f"Message from {user_name}: {text}")
        
        if text == "/start":
            welcome_msg = (
                f"Hi {user_name}! I'm Dagaga's AI assistant.\n"
                "Ask me anything about Dagaga!\n\n"
                "Examples:\n"
                "• What is his email?\n"
                "• Where does he study?\n"
                "• Tech stack?\n"
                "• Grade level?\n"
                "• Favorite movies?\n"
                "• Languages he speaks?\n"
                "• Family?\n"
                "• Blood type?\n"
                "• What blood can he donate/receive?\n"
                "• Tell me about his hobbies"
            )
            self.send_message(chat_id, welcome_msg)
            return
        
        current_time = time.time()
        
        # Check if we should use offline mode
        if self.api_failed and current_time - self.last_api_attempt < self.config.OFFLINE_COOLDOWN:
            reply = "🤖 Offline Mode\n\n"
            reply += self.get_fallback_response(text)
            self.send_message(chat_id, reply)
            return
        
        # Try API
        api_response = self.ask_rag(text)
        
        if api_response:
            self.api_failed = False
            self.send_message(chat_id, api_response)
        else:
            self.api_failed = True
            self.last_api_attempt = current_time
            reply = (
                "⚠️ AI service temporarily unavailable.\n"
                "Using local database instead.\n\n"
            )
            reply += self.get_fallback_response(text)
            reply += "\n\n💡 Tip: You can try again later for AI-powered responses."
            self.send_message(chat_id, reply)
    
    def run(self) -> None:
        """Main bot loop"""
        logger.info("Starting bot...")
        
        # Verify connection
        try:
            response = self.session.get(f"{API_URL}/getMe", timeout=10)
            if response.json().get("ok"):
                bot_username = response.json()['result']['username']
                logger.info(f"Bot connected: @{bot_username}")
            else:
                logger.error("Invalid token!")
                return
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return
        
        logger.info("Bot is ready! Send /start on Telegram")
        
        offset = None
        while True:
            try:
                updates = self.get_updates(offset)
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        offset = update["update_id"] + 1
                        
                        if "message" in update and "text" in update["message"]:
                            msg = update["message"]
                            chat_id = msg["chat"]["id"]
                            text = msg["text"]
                            user_name = msg.get("from", {}).get("first_name", "User")
                            
                            self.handle_message(chat_id, text, user_name)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = TelegramBot(config)
    bot.run()