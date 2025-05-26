import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_USERS, PATH_BEATMAPSETS, PATH_DATA
from os import listdir
from multiprocessing import Pool
from functools import partial
import json

def _process_user_files(file, max_ranked_score, max_score):
    if not file.endswith(".json"): return
    with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
        user = json.load(f)

    id = user["id"]
    name = user["name"]
    tracking = user["tracking"]
    last_score = user["days ago"]
    country = user["country"]
    num_scores = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    ranked_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    total_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    beatmap_plays = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }

    bm_top_scores = {}

    for score in user["scores"].values():
        bid = str(score["bid"])
        msid = score["msid"]
        mfile = f"{msid}.json"
        if mfile in listdir(PATH_BEATMAPSETS):
            with open(f"{PATH_BEATMAPSETS}/{mfile}", "r", encoding='utf-8') as f:
                mapset = json.load(f)

            if bid in mapset["beatmaps"].keys():
                k = str(int(mapset["beatmaps"][bid]["keys"]))
                if k in ["11", "13", "15", "17"]: continue
                num_scores[k] += 1

                if bid in bm_top_scores.keys():
                    if score["score"] > bm_top_scores[bid]["score"]:
                        bm_top_scores[bid]["score"] = score["score"]
                else:
                    bm_top_scores[bid] = {
                        "k":k,
                        "score": score["score"],
                        "status": mapset["beatmaps"][bid]["status"]}

    for bid, val in bm_top_scores.items():
        total_score[val["k"]] += val["score"]
        if val["status"] in [1, 4]:
            ranked_score[val["k"]] += val["score"]

    for msid in user["beatmapsets"].keys():
        file = f"{msid}.json"
        if file in listdir(PATH_BEATMAPSETS):
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding="utf-8") as f:
                mapset = json.load(f)

            for bmid in user["beatmapsets"][msid]:
                beatmap = mapset["beatmaps"][bmid]
                k = str(int(beatmap["keys"]))
                if k in ["11", "13", "15", "17"]: continue
                beatmap_plays[k] += beatmap["total plays"]

    ranked_perc = { k:100*ranked_score[k]/max_ranked_score[k] for k in ["9", "10", "12", "14", "16", "18"]}
    total_perc = { k:100*total_score[k]/max_score[k] for k in ["9", "10", "12", "14", "16", "18"]}

    user_compact = {}
    user_compact["name"] = name
    user_compact["last score"] = last_score
    user_compact["num scores"] = num_scores
    user_compact["ranked score"] = ranked_score
    user_compact["total score"] = total_score
    user_compact["ranked perc"] = ranked_perc
    user_compact["total perc"] = total_perc
    user_compact["beatmap plays"] = beatmap_plays
    user_compact["tracking"] = tracking
    user_compact["country"] = country

    return id, user_compact

def main():
    with open(f"{PATH_DATA}/beatmap_links.json", "r", encoding="utf-8") as f:
        beatmap_links = json.load(f)
    output = f"{PATH_DATA}/users_compact.json"
    users_compact = {}
    users_compact["total"] = 0
    users_compact["active"] = 0
    users_compact["users"] = {}

    max_ranked_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    max_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }

    for file in listdir(PATH_BEATMAPSETS):
        if not file.endswith(".json"): continue
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
            mapset = json.load(f)

        for beatmap in mapset["beatmaps"].values():
            k = str(int(beatmap["keys"]))
            if k in ["11", "13", "15", "17"]: continue

            max_score[k] += 1000000

            if beatmap["status"] in [1, 4]:
                max_ranked_score[k] += 1000000

    files = listdir(PATH_USERS)

    parfunct = partial(_process_user_files, max_ranked_score=max_ranked_score, max_score=max_score)

    with Pool() as pool:
        results = pool.map(parfunct, files)

    users_compact["users"] = dict(results)

    for user in users_compact["users"].values():
        users_compact["total"] += 1
        if user["tracking"]:
            users_compact["active"] += 1

    with open(output, "w", encoding="utf-8") as f:
        json.dump(users_compact, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()

