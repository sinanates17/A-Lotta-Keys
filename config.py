from dotenv import load_dotenv
import os

load_dotenv()

OSU_API_ID = os.getenv("OSU_API_KEY")
OSU_API_SECRET = os.getenv("OSU_API_SECRET")
OSU_API_VERSION = os.getenv("OSU_API_VERSION")
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")