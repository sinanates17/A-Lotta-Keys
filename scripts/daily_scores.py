import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone
from data.utils import Helper
from config import PATH_SCORES, PATH_USERS
from os import listdir
import json

def main():
    helper = Helper()
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%d%H%M%S")
    output = f"scores_{now}.json"
    cum_scores = { "timestamp": now }

    for file in listdir(PATH_USERS)[0:50]:
        if not file.endswith(".json"): continue
        with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
            user = json.load(f)
        
        if user['tracking']:
            scores = helper.user_scores_recent(user_id=user["id"])
            for score in scores:
                if score.beatmap.cs > 8 and score.beatmap.mode.value == "mania":
                    score_dict = Helper.score_to_dict(score)
                    id = f"{score_dict['uid']}{score_dict['time']}"
                    cum_scores[id] = score_dict
    
    with open(f"{PATH_SCORES}/{output}", "w", encoding='utf-8') as f:
        json.dump(cum_scores, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()