import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from data.utils import Helper
from config import PATH_SCORES, PATH_USERS, PATH_BEATMAPSETS
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
        new_uids = []

        for uid in uids:
            c = False
            for file in listdir(PATH_USERS):
                with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                    user = json.load(f)
                
                if user["id"] == uid:
                    c = True
                    break

            if c: continue
            new_uids.append(uid)

        new_users = helper.users(new_uids)

        for user in new_users:
            user_dict = Helper.user_to_dict(user)
            name = user.username
            output = f"{PATH_USERS}/{name}.json"

            with open (output, "w", encoding='utf-8') as f:
                json.dump(user_dict, f, ensure_ascii=False, indent=4)

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

    def _update_play_history():
        uid_mapsets = {}

        for file in listdir(PATH_BEATMAPSETS):
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                mapset = json.load(f)
            msid = mapset["id"]

            for bid in mapset["beatmaps"].keys():

                uid = mapset["beatmaps"][bid]["mapper id"]
                uid_mapset = uid_mapsets.get(uid, {})

                uid_mapset[msid] = uid_mapset.get(msid, [])
                uid_mapset[msid].append(bid)
                uid_mapsets[uid] = uid_mapset

        for file in listdir(PATH_USERS):
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user = json.load(f)

            uid = user["id"]
            uids.append(uid)
            total_plays = 0
            user["beatmapsets"] = uid_mapsets.get(uid, {})
            if user["beatmapsets"] == {}: continue

            for bfile in listdir(PATH_BEATMAPSETS):
                with open(f"{PATH_BEATMAPSETS}/{bfile}", "r", encoding='utf-8') as f:
                    mapset_json = json.load(f)
                
                msid = mapset_json["id"]
                if msid in uid_mapsets[uid].keys():
                    for bid, diff in mapset_json["beatmaps"].items():
                        if bid in uid_mapsets[uid][msid]:
                            total_plays += mapset_json["beatmaps"][bid]["total plays"]

            user["beatmap plays history"][now] = total_plays

            with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=4)

    def _update_name_url():
        users = helper.users(uids)

        for file in listdir(PATH_USERS):
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user_dict = json.load(f)
            
            uid = user_dict["id"]
            
            for user in users:
                if user.id == uid:
                    user_dict_new = Helper.user_to_dict(user)
                    user_dict["name"] = user_dict_new["name"]
                    user_dict["avatar url"] = user_dict_new["avatar url"]

    helper = Helper()
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%dH%M%S")
    uids = []
    
    _initialize_new_users()
    _update_scores()
    _update_play_history

if __name__ == '__main__':
    main()