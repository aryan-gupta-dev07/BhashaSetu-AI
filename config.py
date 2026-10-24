import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=True)

GNANI_API_KEY = os.getenv("GNANI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


def validate_config():
    """Validate the required API configuration."""

    missing_keys = []

    if not GNANI_API_KEY:
        missing_keys.append("GNANI_API_KEY")

    if not GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")

    if missing_keys:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing_keys)
        )