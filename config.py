from dotenv import load_dotenv
import os

load_dotenv()

OSU_API_ID = os.getenv("OSU_API_ID")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")