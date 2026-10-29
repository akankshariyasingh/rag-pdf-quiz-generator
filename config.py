
import os
from pathlib import Path

from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from the project's .env file
load_dotenv(BASE_DIR / ".env", override=True)

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Use the model name configured in .env.
# The fallback is used only when GEMINI_MODEL is not set.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
).strip()

# ChromaDB persistent storage
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# PDF processing configuration
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Quiz configuration
QUIZ_QUESTION_COUNT = 5
OPTIONS_PER_QUESTION = 4

# Retrieval configuration
RETRIEVAL_TOP_K = 5

# Create the database directory if it doesn't exist
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)


def validate_gemini_config():
    """Validate that the Gemini API key is configured."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the project's .env file."
        )

    if len(GEMINI_API_KEY) < 20:
        raise ValueError(
            "GEMINI_API_KEY appears incomplete. "
            "Check the key in your .env file."
        )
