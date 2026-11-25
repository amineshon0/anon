import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

_raw_admins = os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", "")).strip()
ADMIN_IDS: set[int] = {
    int(uid.strip())
    for uid in _raw_admins.split(",")
    if uid.strip().isdigit()
}

DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "data/bot.db"))
