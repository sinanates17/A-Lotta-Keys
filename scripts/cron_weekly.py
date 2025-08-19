"""
This script is meant to be run weekly.

Parent script: cron_weekly.py
    - Weekly data backup

"""

import subprocess
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone
from config import PATH_DATA, PATH_DATA_BACKUP

def main():
    now = datetime.now(timezone.utc)
    now = now.strftime("%m-%d-%y_%H-%M-%S")
    path_archive = f"/{PATH_DATA_BACKUP}/data_{now}.tar.xz"
    path_data = f"/{PATH_DATA}"

    cmd = [
        "tar",
        "-c", 
        "-I", 
        "xz -6", 
        "-f", 
        path_archive,  
        path_data 
    ]

    subprocess.run(cmd)

if __name__ == "__main__":
    main()