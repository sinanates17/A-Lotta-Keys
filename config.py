from dotenv import load_dotenv
import os
import sys

from pathlib import Path
dotenv_path = Path(__file__).resolve().parent / ".env"
#print("=== CONFIG IMPORTED ===", file=sys.stderr)
#print(f"DEBUG: dotenv_path used = {dotenv_path}", file=sys.stderr)
load_dotenv(dotenv_path)

OSU_API_ID = os.getenv("OSU_API_ID")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

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

#print("DEBUG: ENV VALUE =", PATH_ROOT, file=sys.stderr)