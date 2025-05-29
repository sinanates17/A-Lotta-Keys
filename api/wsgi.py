from app import app
from dotenv import load_dotenv
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

load_dotenv()
application = app
#For production