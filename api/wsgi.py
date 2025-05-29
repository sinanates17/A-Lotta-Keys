import os
from dotenv import load_dotenv

try:
    load_dotenv("/home/sinanates/Github/A-Lotta-Keys/.env")
except Exception as e:
    with open("/tmp/wsgi_error.log", "w") as f:
        f.write(f"Failed to load .env: {e}\n")

try:
    from app import app as application
except Exception as e:
    with open("/tmp/wsgi_error.log", "a") as f:
        f.write(f"Failed to load Flask app: {e}\n")