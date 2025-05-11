from dotenv import load_dotenv
import os

load_dotenv()

OSU_API_ID = os.getenv("OSU_API_ID")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")

PATH_USERS = os.getenv("PATH_USERS")
PATH_BEATMAPSETS = os.getenv("PATH_BEATMAPSETS")
PATH_SCORES = os.getenv("PATH_SCORES")

REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL"))

DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")