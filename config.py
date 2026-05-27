import os

from dotenv import load_dotenv


load_dotenv()


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = _get_env("BOT_TOKEN")
GOOGLE_API_KEY = _get_env("GOOGLE_API_KEY")

