"""
This script and its children are meant to be run daily.

Parent script: cron_daily.py

Child script 1: daily_scores.py
    - For every user.json with Tracking: True, request + dump all recent scores

Child script 2: daily_beatmapsets.py
    - Request every 9K+ beatmapset
    - Initialize a new .json for any newly uploaded maps.
    - Check all maps for updates:
        - Changes in metadata
        - Favorite count
        - New difficulties
        - Changes in difficulties
            - Diff name
            - SR
            - BPM
            - Mapper (assigned GDs, this will require some extra logic)
            - Last updated
            - Time ranked
            - Status
            - Gained a leaderboard?
            - Drain time
            - Circle and slider count
            - Total plays and passes, plus historical
    - Go through the daily scores dump and: 
        - Append players to the beatmaps players list if they set a first.
        - Append new scores to the scores list

Child script 3: daily_users.py
    - Crudely check for new activity from inactive users:
        - Request top scores from last 10 leaderboard mapsets, set all included users' tracking to True
        - False positives will be corrected by the next steps
    - Go through the daily scores dump and:
        - Generate a new .json for any new users.
    - For each user:
        - Update name and avatar url even tho these are unlikely to change.
        - Append new scores to the user's scores
        - Add any new beatmaps this user mapped and remove ones where the owner might have changed
        - Sum the user's beatmap plays and append to the timeline
        - Find out the time since last score. Stop tracking if >60 days
"""

import subprocess
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_PYTHON, PATH_ROOT

def main():
    subprocess.run([PATH_PYTHON, "scripts/daily_scores.py"], cwd=PATH_ROOT)
    subprocess.run([PATH_PYTHON, "scripts/daily_beatmapsets.py"], cwd=PATH_ROOT)
    subprocess.run([PATH_PYTHON, "scripts/daily_beatmaps_compact.py"], cwd=PATH_ROOT)
    subprocess.run([PATH_PYTHON, "scripts/daily_users.py"], cwd=PATH_ROOT)
    subprocess.run([PATH_PYTHON, "scripts/daily_users_compact.py"], cwd=PATH_ROOT)
    subprocess.run([PATH_PYTHON, "scripts/calculate_pp_history.py"], cwd=PATH_ROOT)

if __name__ == "__main__":
    main()
