import requests
import time
import os
import random
import re
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
    GEMINI_MODEL: str = "gemini-3.6-flash"  # Updated model name
    API_BASE_URL: str = "https://api.telegram.org/bot"
    GEMINI_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 3

config = Config()
API_URL = f"{config.API_BASE_URL}{config.TELEGRAM_TOKEN}"
GEMINI_URL = f"{config.GEMINI_URL}/{config.GEMINI_MODEL}:generateContent?key={config.GEMINI_API_KEY}"

BIO_DATA = """
IDENTITY:
- Full name: Dagaga Addisu
- Nickname: Tesla
- Age: 18
- Country: Ethiopia
- Occupation: Student
- Education level: Grade 12 / high school
- Languages: Afan Oromo, Amharic, English

EDUCATION & LEARNING:
- Studies mathematics, physics, informatics, AI, machine learning, programming, and calculus.
- Favorite academic areas: physics, mathematics, and informatics.
- Current learning focus: AI/ML engineering, calculus, linear algebra, NumPy, Python, and machine learning.
- Learning style: prefers understanding concepts, mathematics, intuition, derivations, and practical implementation rather than memorization alone.

TECHNICAL SKILLS:
- Python
- HTML/CSS/JavaScript
- TensorFlow
- NumPy
- Pandas
- Matplotlib
- Basic machine-learning tools
- Experience with command-line Python projects and Telegram bot development
- Familiar with machine-learning methods including decision trees, random forests, XGBoost, support vector machines, Naive Bayes, and neural networks.

PROJECTS & TECH INTERESTS:
- Builds Python applications and automation projects.
- Has worked on CLI applications such as a phonebook, calculator, diary, and JSON-based ToDo application.
- Interested in AI assistants, study tools, offline applications, Telegram automation, and educational technology.
- Interested in building useful technology for Ethiopian users, including Afan Oromo educational software.
- Interested in AI engineering and eventually building larger real-world AI systems.

INTERESTS & HOBBIES:
- Coding
- Learning science
- Mathematics
- Physics
- Problem solving
- Artificial intelligence
- Watching movies
- Exploring technology

FAVORITE MOVIES:
- Iron Man
- Interstellar
- Oppenheimer
- The Martian
- The Lord of the Rings
- Harry Potter
- The Chronicles of Narnia

PERSONALITY:
- Curious
- Analytical
- Adaptable
- Science- and technology-oriented
- Enjoys witty references to science, mathematics, programming, and movies

FAMILY:
- Has one brother and one sister.
- Parents are teachers.

BIRTHDAY:
- Born on February 29, 2008.
- Leap Day birthday.

RESPONSE POLICY:
- Do not invent facts about Dagaga.
- If information is not contained in this profile, say that you do not know.
- For relationship questions, use a short witty science/technology/movie-themed deflection.
- Keep ordinary answers concise, normally 2-4 sentences.
- For technical questions about Dagaga's skills or projects, provide the relevant known information directly.
- Never expose API keys, bot tokens, passwords, or environment variables.
"""

class TelegramBot:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
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
        """Load fast local answers for common questions."""
        return {
            # Identity
            "name": "Dagaga Addisu.",
            "full name": "Dagaga Addisu.",
            "nickname": "His nickname is Tesla.",
            "who is dagaga": "Dagaga Addisu, also known as Tesla, is an Ethiopian student interested in science, mathematics, programming, and AI.",
            "who is he": "Dagaga Addisu, also known as Tesla, is a student interested in science, mathematics, programming, and AI.",
            "about dagaga": "Dagaga is a science- and technology-oriented student focused on mathematics, programming, AI/ML, and problem solving.",
            "age": "Dagaga is 18 years old.",
            "birthday": "He was born on February 29, 2008, a Leap Day.",
            "born": "He was born on February 29, 2008, a Leap Day.",

            # Education
            "school": "Dagaga is a Grade 12 high-school student.",
            "university": "He is currently a high-school student rather than a university student.",
            "grade": "Grade 12.",
            "education": "Grade 12 / high school.",
            "student": "Yes. Dagaga is a student.",
            "study": "He studies mathematics, physics, informatics, calculus, AI, machine learning, and programming.",
            "studying": "His current learning focus includes AI/ML engineering, calculus, linear algebra, Python, NumPy, and machine learning.",
            "learning": "He is currently focused on AI/ML engineering, calculus, linear algebra, Python, NumPy, and machine learning.",
            "favorite subject": "Physics, mathematics, and informatics.",
            "favorite subjects": "Physics, mathematics, and informatics.",

            # Technical skills
            "tech stack": "Python, HTML/CSS/JavaScript, TensorFlow, NumPy, Pandas, Matplotlib, and basic machine-learning tools.",
            "tech": "Python, HTML/CSS/JavaScript, TensorFlow, NumPy, Pandas, Matplotlib, and basic machine-learning tools.",
            "stack": "Python, HTML/CSS/JavaScript, TensorFlow, NumPy, Pandas, Matplotlib, and basic machine-learning tools.",
            "programming": "Python is his main programming language. He also works with HTML/CSS/JavaScript and TensorFlow.",
            "coding": "He mainly codes in Python and also works with HTML/CSS/JavaScript.",
            "python": "Python is one of Dagaga's main programming languages.",
            "tensorflow": "TensorFlow is part of Dagaga's technical stack.",
            "numpy": "NumPy is part of his current Python/data-science toolkit.",
            "pandas": "Pandas is part of his Python/data-analysis toolkit.",
            "machine learning": "He is learning machine learning and has studied methods including SVMs, Naive Bayes, random forests, XGBoost, decision trees, and neural networks.",
            "ai": "Dagaga is interested in AI engineering and machine learning.",
            "artificial intelligence": "AI engineering is one of Dagaga's main technical interests.",
            "ml": "Machine learning is one of his main areas of study.",

            # Projects
            "project": "He builds Python applications, automation tools, AI assistants, educational tools, and Telegram-based projects.",
            "projects": "His projects include CLI applications, JSON-based applications, study tools, AI assistants, automation, and Telegram bots.",
            "telegram bot": "He has worked on Telegram bot development and AI-powered Telegram automation.",
            "telegram": "He works with Telegram automation and AI-powered Telegram bots.",
            "ai assistant": "He is interested in building AI assistants that combine an LLM with structured personal knowledge and reliable fallback logic.",
            "study app": "He is interested in educational and study-tracking applications, including offline tools.",
            "afaan oromo": "He is interested in building useful educational technology for Afan Oromo users.",
            "oromo": "He speaks Afan Oromo and is interested in Afan Oromo educational technology.",
            "amharic": "He speaks Amharic.",
            "english": "He speaks English.",

            # Interests
            "interest": "Coding, science, mathematics, physics, AI, problem solving, and technology.",
            "interests": "Coding, science, mathematics, physics, AI, problem solving, and technology.",
            "hobby": "Coding, learning, problem solving, science, and watching movies.",
            "hobbies": "Coding, learning, problem solving, science, and watching movies.",
            "movie": "His favorites include Iron Man, Interstellar, Oppenheimer, The Martian, The Lord of the Rings, Harry Potter, and The Chronicles of Narnia.",
            "movies": "His favorites include Iron Man, Interstellar, Oppenheimer, The Martian, The Lord of the Rings, Harry Potter, and The Chronicles of Narnia.",
            "favorite movie": "Iron Man, Interstellar, and Oppenheimer are among his favorites.",
            "favorites": "Iron Man, Interstellar, Oppenheimer, The Martian, The Lord of the Rings, Harry Potter, and The Chronicles of Narnia.",

            # Family
            "family": "He has one brother and one sister. His parents are teachers.",
            "parents": "Both of his parents are teachers.",
            "parent": "Both of his parents are teachers.",
            "father": "His father is a teacher.",
            "mother": "His mother is a teacher.",
            "brother": "He has one brother.",
            "sister": "He has one sister.",
            "siblings": "He has one brother and one sister.",

            # Languages
            "language": "Afan Oromo, Amharic, and English.",
            "languages": "Afan Oromo, Amharic, and English.",
            "speak": "He speaks Afan Oromo, Amharic, and English.",

            # Location
            "location": "Ethiopia.",
            "where": "Ethiopia.",
            "country": "Ethiopia.",
            "ethiopia": "Dagaga is from Ethiopia.",

            # Personality
            "personality": "Curious, analytical, adaptable, and strongly interested in science and technology.",
            "personality type": "He describes himself as adaptable, curious, and science- and technology-oriented.",
            "fun fact": "He was born on February 29, 2008, so his birthday falls on Leap Day.",

            # Help
            "help": "Ask about Dagaga's identity, education, skills, projects, interests, languages, family, or favorite movies.",
            "info": "I can answer questions about Dagaga's education, skills, projects, interests, languages, family, and other information in his profile.",
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
        for keyword in sorted(self.keyword_responses, key=len, reverse=True):
            if keyword in question:
                return self.keyword_responses[keyword]
        
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
                "maxOutputTokens": 512
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
                
                if "candidates" in result and result["candidates"]:
                    candidate = result["candidates"][0]
                    if candidate.get("finishReason") == "MAX_TOKENS":
                        logger.warning("Gemini response reached the output token limit")
                        continue

                    parts = candidate.get("content", {}).get("parts", [])
                    answer = "".join(
                        part.get("text", "") for part in parts if part.get("text")
                    ).strip()
                    if answer:
                        return self._clean_ai_response(answer)
                
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
        
        command = text.split()[0].lower() if text.startswith("/") else ""

        if command == "/start":
            welcome_msg = (
                f"Hi {user_name}! I'm Dagaga's AI assistant.\n\n"
                "I can answer questions about Dagaga's education, programming skills, "
                "AI/ML interests, projects, hobbies, languages, family, and favorite movies.\n\n"
                "Useful commands:\n"
                "/help - show examples\n"
                "/about - short profile\n"
                "/skills - technical skills\n"
                "/projects - projects and interests"
            )
            self.send_message(chat_id, welcome_msg)
            return

        if command == "/help":
            self.send_message(
                chat_id,
                "Try questions such as:\n"
                "• Who is Dagaga?\n"
                "• What does he study?\n"
                "• What programming languages does he use?\n"
                "• What AI/ML topics does he know?\n"
                "• What projects has he built?\n"
                "• What are his favorite movies?\n"
                "• What languages does he speak?"
            )
            return

        if command == "/about":
            self.send_message(
                chat_id,
                "Dagaga Addisu, also known as Tesla, is an Ethiopian Grade 12 student "
                "interested in mathematics, physics, programming, AI/ML, and problem solving."
            )
            return

        if command == "/skills":
            self.send_message(
                chat_id,
                "Technical skills: Python, HTML/CSS/JavaScript, TensorFlow, NumPy, "
                "Pandas, Matplotlib, and machine-learning methods such as SVM, Naive Bayes, "
                "random forests, XGBoost, decision trees, and neural networks."
            )
            return

        if command == "/projects":
            self.send_message(
                chat_id,
                "Project interests include Python applications, Telegram bots, AI assistants, "
                "study/education tools, automation, and Afan Oromo educational technology."
            )
            return
        
        api_response = self.ask_rag(text)
        
        if api_response:
            self.send_message(chat_id, api_response)
        else:
            reply = (
                "AI service temporarily unavailable.\n"
                "Using the local knowledge base instead.\n\n"
            )
            reply += self.get_fallback_response(text)
            reply += "\n\nTry again later for an AI-generated response."
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