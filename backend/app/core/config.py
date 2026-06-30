from pathlib import Path

from dotenv import load_dotenv

# Resolve .env relative to the backend root (one level above app/)
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)
