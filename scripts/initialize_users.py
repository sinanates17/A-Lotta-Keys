import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.utils import Helper
from config import PATH_SCORES, PATH_USERS
from os import listdir
import json

def main():
    users = []
    helper = Helper()
    for file in listdir(PATH_SCORES):
        with open(f"{PATH_SCORES}/{file}", "r", encoding='utf-8') as f:
            scores = json.load(f)
        
        for score in scores.values():
            users.append(score.get('uid'))

    users = list(set(users))
    users = helper.users(users)
    for user in users:
        user_dict = Helper.user_to_dict(user)
        name = user.username
        output = f"{PATH_USERS}/{name}.json"

        with open (output, "w", encoding='utf-8') as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()