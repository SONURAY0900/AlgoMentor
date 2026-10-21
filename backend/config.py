import os
from dotenv import load_dotenv

# Load backend/.env regardless of the working directory the server is started from
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# -------- LLM CONFIG (Groq) --------
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))
# Retries wait for the delay Groq asks for (free tier has a tokens-per-minute limit)
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "6"))

# -------- DATABASE CONFIG --------
# Set DB_HOST (+ the others) to use MySQL / TiDB Cloud; otherwise a local SQLite file is used.
DB_HOST = os.getenv("DB_HOST", "").strip()
DB_PORT = int(os.getenv("DB_PORT", "4000"))
DB_USER = os.getenv("DB_USER", "").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "algomentor").strip()
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "algomentor.db")

# Bump this when prompts change so old cached answers are not reused
CACHE_VERSION = "1"
HISTORY_LIMIT = 30

# -------- APP CONFIG --------
SUPPORTED_LANGUAGES = ["Python", "Java", "C", "C++"]
DEFAULT_LANGUAGE = "Python"
MAX_INPUT_CHARS = 20000
