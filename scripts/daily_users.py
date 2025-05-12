import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from data.utils import Helper
from config import PATH_SCORES, PATH_USERS, PATH_BEATMAPSETS
from os import listdir
import json

def main():
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
                if str(uid) in file and file.endswith(".json"): 
                    c = True
                    break

            if c: continue
            new_uids.append(uid)

        new_users = helper.users(new_uids)

        for user in new_users:
            user_dict = Helper.user_to_dict(user)
            id = user.id
            output = f"{PATH_USERS}/{id}.json"

            with open (output, "w", encoding='utf-8') as f:
                json.dump(user_dict, f, ensure_ascii=False, indent=4)

    def _update_scores():
        cutoff = datetime.now(timezone.utc) - timedelta(days=2)
        cutoff = cutoff.strftime("%y%m%d%H%M%S")
        uids_scores = {}

        for file in listdir(PATH_SCORES):
            if not file.endswith(".json"): continue
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
                if str(uid) in file and file.endswith(".json"):
                    with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                        user = json.load(f)
                    
                    user["scores"] |= scores
                    with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                        json.dump(user, f, ensure_ascii=False, indent=4)

                    break

    def _update_mapsets_playhistory():
        uids_mapsets = {}

        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                mapset = json.load(f)
            msid = mapset["id"]

            for bid in mapset["beatmaps"].keys():

                uid = mapset["beatmaps"][bid]["mapper id"]
                uid_mapsets = uids_mapsets.get(uid, {})

                uid_mapsets[msid] = uid_mapsets.get(msid, [])
                uid_mapsets[msid].append(bid)
                uids_mapsets[uid] = uid_mapsets

        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user = json.load(f)

            uid = user["id"]
            uids.append(uid)
            total_plays = 0
            user["beatmapsets"] = uids_mapsets.get(uid, {}) #This should accordingly update difficulty owner changes
            if user["beatmapsets"] == {}: continue

            for msid in user["beatmapsets"].keys():
                with open(f"{PATH_BEATMAPSETS}/{msid}.json", "r", encoding='utf-8') as f:
                    mapset_json = json.load(f)
                    
                for bid in user["beatmapsets"][msid]:
                    total_plays += mapset_json["beatmaps"][bid]["total plays"]

            user["beatmap plays history"][now] = total_plays

            with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=4)

    def _update_name_url():
        users = helper.users(uids)

        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user_dict = json.load(f)
            
            uid = user_dict["id"]
            
            for user in users:
                if user.id == uid:
                    user_dict_new = Helper.user_to_dict(user)
                    user_dict["name"] = user_dict_new["name"]
                    user_dict["avatar url"] = user_dict_new["avatar url"]

                    with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                        json.dump(user_dict, f, ensure_ascii=False, indent=4)

    helper = Helper()
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%d%H%M%S")
    uids = []
    
    _initialize_new_users()
    _update_scores()
    _update_mapsets_playhistory()
    _update_name_url()

if __name__ == '__main__':
    main()