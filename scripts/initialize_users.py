import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from datetime import datetime, timezone
from config import PATH_SCORES, PATH_USERS
from os import listdir
import json

def main():
    users = []
    helper = Helper()
    for file in listdir(PATH_SCORES):
        if not file.endswith(".json"): continue
        with open(f"{PATH_SCORES}/{file}", "r", encoding='utf-8') as f:
            scores = json.load(f)
        
        for id, score in scores.items():
            if id == "timestamp": continue
            users.append(score.get('uid'))

    users = list(set(users))
    users = helper.users(users)
    for user in users:
        user_dict = Helper.user_to_dict(user)
        id = user.id
        output = f"{PATH_USERS}/{id}.json"

        with open (output, "w", encoding='utf-8') as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()