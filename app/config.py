import os

from dotenv import load_dotenv

load_dotenv()


def _env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


GOOGLE_GENAI_USE_VERTEXAI: bool = _env_flag("GOOGLE_GENAI_USE_VERTEXAI", True)
GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./wordgame.db")
POINTS_PER_CORRECT: int = int(os.getenv("POINTS_PER_CORRECT", "10"))
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "c6B7LIWri0Y1ZhWVF8Mm")
