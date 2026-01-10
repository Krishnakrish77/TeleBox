import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/telebox")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512 * 1024))
