import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from data.utils import Helper
from config import PATH_SCORES, PATH_USERS
from os import listdir
import json

def main():

    def _old_version(id: int) -> dict:
        for file in listdir(PATH_USERS):
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                result = json.load(f)
            
            if result["id"] == id:
                return result
        
        return None

    def _initialize_new_users():
        bids = helper.recent_beatmap_ids()
        uids = []
        for bid in bids:
            uids += helper.beatmap_player_ids(beatmap_id=bid)

        uids = list(set(uids))

        for uid in uids:
            pass

    def _update_scores():
        cutoff = datetime.now(timezone.utc) - timedelta(days=2)
        cutoff = cutoff.strftime("%y%m%d%H%M%S")
        uids_scores = {}

        for file in listdir(PATH_SCORES):
            with open(f"{PATH_SCORES}/{file}", "r", encoding='utf-8') as f:
                scores = json.load(f)

            if int(scores["timestamp"]) > int(cutoff):
                for sid, score in scores.items():
                    if sid == "timestamp": continue

                    uid = score["uid"]
                    uid_scores = uids_scores.get(uid, {})
                    uid_scores[sid] = score
                    uids_scores[uid] = uid_scores

        for uid, scores in uids_scores.items():
            for file in listdir(PATH_USERS):
                with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                    user = json.load(f)
                
                if uid == user["id"]:
                    user["scores"] |= scores

                    with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                        json.dump(user, f, ensure_ascii=False, indent=4)

                    break

    helper = Helper()
    mapsets = helper.cum_search_beatmapsets(
        query="keys>8", 
        explicit_content="show", 
        category="any")
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%dH%M%S")
    
    _initialize_new_users()
    _update_scores()

if __name__ == '__main__':
    main()