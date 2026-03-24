import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

DB_PATH = os.getenv("POLYCITY_DB", str(PROJECT_ROOT / "polycity_memory.db"))
SEED_PATH = Path(os.getenv("POLYCITY_SEED", str(PROJECT_ROOT / "data" / "seed_hotels.json")))

HTTP_TIMEOUT_S = float(os.getenv("POLYCITY_HTTP_TIMEOUT", "15"))
MAX_FETCH_CHARS = int(os.getenv("POLYCITY_MAX_FETCH_CHARS", "12000"))
