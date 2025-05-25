import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from datetime import datetime, timezone
from config import PATH_SCORES, PATH_BEATMAPSETS, PATH_USERS
from os import listdir
import json

def main():
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%y%m%d%H%M%S")
    helper = Helper()

    for sfile in listdir(PATH_SCORES):
        if not sfile.endswith(".json"): continue
        uid_scores = {}
        bid_scores = {}
        uid_mapsets = {}

        with open(f"{PATH_SCORES}/{sfile}", "r", encoding='utf-8') as f:
            scores = json.load(f)

        for id, score in scores.items():
            if id == 'timestamp': continue
            uid = score['uid']
            bid = score['bid']
            u = uid_scores.get(uid, {})
            b = bid_scores.get(bid, {})
            uid_scores[uid] = u
            bid_scores[bid] = b
            uid_scores[uid][id] = score
            bid_scores[bid][id] = score

        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user = json.load(f)

            uid = user['id']
            user['scores'] |= uid_scores[uid]

            with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=4)

        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                mapset = json.load(f)

            for bid in mapset["beatmaps"].keys():
                mapset["beatmaps"][bid]['scores'] |= bid_scores.get(int(bid), {})

                sid = mapset["id"]
                uid = mapset["beatmaps"][bid]["mapper id"]
                uid_mapset = uid_mapsets.get(uid, {})

                uid_mapset[sid] = uid_mapset.get(sid, [])
                uid_mapset[sid].append(bid)
                uid_mapsets[uid] = uid_mapset

            with open(f"{PATH_BEATMAPSETS}/{file}", "w", encoding='utf-8') as f:
                json.dump(mapset, f, ensure_ascii=False, indent=4)

        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user = json.load(f)

            recent = datetime(year=2013, month=1, day=1, tzinfo=timezone.utc)
            for score in user["scores"].values():
                t = datetime.strptime(score["time"], "%y%m%d%H%M%S")
                t = t.replace(tzinfo=timezone.utc)
                if t > recent:
                    recent = t
            difference = (now - recent).days
            user["days ago"] = difference

            if difference > 60:
                user["tracking"] = False

            uid = user["id"]
            total_plays = 0
            user["beatmapsets"] = uid_mapsets.get(uid, {})
            if user["beatmapsets"] == {}: 
                with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                    json.dump(user, f, ensure_ascii=False, indent=4)
                continue

            for bfile in listdir(PATH_BEATMAPSETS):
                if not bfile.endswith(".json"): continue
                with open(f"{PATH_BEATMAPSETS}/{bfile}", "r", encoding='utf-8') as f:
                    mapset_json = json.load(f)
                
                sid = mapset_json["id"]
                if sid in uid_mapsets[uid].keys():
                    for bid, diff in mapset_json["beatmaps"].items():
                        if bid in uid_mapsets[uid][sid]:
                            total_plays += mapset_json["beatmaps"][bid]["total plays"]

            user["beatmap plays history"][now_str] = total_plays

            with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()