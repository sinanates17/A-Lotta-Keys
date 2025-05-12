"""
This script and its children are meant to be run weekly.

Parent script: cron_weekly.py

Child script 1: weekly_backup.py
-

"""

import subprocess
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PYTHON_PATH

def main():
    pass

if __name__ == "main":
    main()