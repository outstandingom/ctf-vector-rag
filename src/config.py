import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", "7860"))
DB_FILE_PATH = os.getenv("DB_FILE_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "ctf_knowledge.json"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
