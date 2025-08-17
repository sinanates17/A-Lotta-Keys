from dotenv import load_dotenv
import os
import sys
import pprint

from pathlib import Path
dotenv_path = Path(__file__).resolve().parent / ".env"
if not dotenv_path.exists():
    print(f"WARNING: .env not found at {dotenv_path}", file=sys.stderr)
#print("=== CONFIG IMPORTED ===", file=sys.stderr)
#print(f"DEBUG: dotenv_path used = {dotenv_path}", file=sys.stderr)
load_dotenv(dotenv_path)

OSU_API_ID = os.getenv("OSU_API_ID")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")
OSU_REDIRECT_URI = os.getenv("OSU_REDIRECT_URI")

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BOT_REDIRECT_URI = os.getenv("BOT_REDIRECT_URI")

PATH_USERS = f"{os.getenv("PATH_DATA")}/users"
PATH_BEATMAPSETS = f"{os.getenv("PATH_DATA")}/beatmapsets"
PATH_SCORES = f"{os.getenv("PATH_DATA")}/scores"
PATH_DATA = f"{os.getenv("PATH_DATA")}"
PATH_SCORES_ARCHIVE = f"{os.getenv("PATH_DATA")}/scores/archive"
PATH_DATA_BACKUP = os.getenv("PATH_DATA_BACKUP")
PATH_DISCORD_BOT = f"{os.getenv("PATH_ROOT")}/discord_bot"

REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL", "2.5"))

PATH_PYTHON = f"{os.getenv("PATH_VENV")}/bin/python"
PATH_ROOT = os.getenv("PATH_ROOT")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

pprint.pprint(dict(os.environ))