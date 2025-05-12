from dotenv import load_dotenv
import os

load_dotenv()

OSU_API_ID = os.getenv("OSU_API_ID")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")

PATH_USERS = f"{os.getenv("PATH_DATA")}/users"
PATH_BEATMAPSETS = f"{os.getenv("PATH_DATA")}/beatmapsets"
PATH_SCORES = f"{os.getenv("PATH_DATA")}/scores"
PATH_DATA = f"{os.getenv("PATH_DATA")}"
PATH_SCORES_ARCHIVE = f"{os.getenv("PATH_DATA")}/scores/archive"
PATH_DATA_BACKUP = os.getenv("PATH_DATA_BACKUP")

REQUEST_INTERVAL = float(os.getenv("REQUEST_INTERVAL"))

PATH_PYTHON = os.getenv("PYTHON_PATH")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")