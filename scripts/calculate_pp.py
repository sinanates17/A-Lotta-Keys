"""
This is a manually-run script to retroactively calculate pp for existing scores
that don't have pp values.
"""

import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from config import PATH_USERS, PATH_BEATMAPSETS, PATH_SCORES
from os import listdir
import json

def main():
    """
    user_scores = {}

    for file in listdir(PATH_BEATMAPSETS):
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding="utf-8") as f:
            mapset = json.load(f)

        for bmid, beatmap in mapset["beatmaps"].items():
            sr = beatmap["sr"]

            for sid, score in beatmap["scores"].items():
                if score["pp"] is None:
                    pp = Helper.calculate_pp(score, sr)
                    score["pp"] = pp

                    uid = score["uid"]
                    user_scores[uid] = user_scores.get(uid, {})
                    user_scores[uid] |= { sid: pp }

        with open(f"{PATH_BEATMAPSETS}/{file}", "w", encoding="utf-8") as f:
            json.dump(mapset, f, ensure_ascii=False, indent=4)

    for uid, pairs in user_scores.items():
        try:
            with open(f"{PATH_USERS}/{uid}.json", "r", encoding="utf-8") as f:
                user = json.load(f)
        except:
            continue

        for sid, pp in pairs.items():
            if sid in list(user["scores"].keys()):
                user["scores"][sid]["pp"] = pp

        with open(f"{PATH_USERS}/{uid}.json", "w", encoding="utf-8") as f:
            json.dump(user, f, ensure_ascii=False, indent=4)
    """
    links = Helper.load_beatmap_links()

    for file in listdir(PATH_SCORES):
        if not file.endswith(".json"): continue
        with open(f"{PATH_SCORES}/{file}", "r", encoding="utf-8") as f:
            scores = json.load(f)

        for sid, score in scores.items():
            if sid == "timestamp": 
                continue

            if score["pp"] is None:
                score["pp"] = Helper.calculate_pp(score)

            score["pp"] = round(score["pp"], 2)

            try:
                if score["msid"] is None:
                    score["msid"] = links[score["bid"]]
            except:
                pass
        
        with open(f"{PATH_SCORES}/{file}", "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()