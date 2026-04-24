import os
from dotenv import load_dotenv

load_dotenv(os.getenv("ENV_FILE", ".env"), override=True)

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./job_assistant.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAX_JOBS_PER_RUN = int(os.getenv("MAX_JOBS_PER_RUN", "200"))
