import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_USERS, PATH_BEATMAPSETS, PATH_DATA
from os import listdir
import json

def main():
    output = f"{PATH_DATA}/users_compact.json"
    users_compact = {}
    users_compact["users"]
    users_compact["total"] = 0
    users_compact["active"] = 0

    max_ranked_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    max_score = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }

    for file in listdir(PATH_BEATMAPSETS):
        if not file.endswith(".json"): continue
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
            mapset = json.load(f)

        for beatmap in mapset["beatmaps"].values():
            k = str(beatmap["keys"])
            max_score[k] += 1000000

            if beatmap["status"] in [1, 4]:
                max_ranked_score[k] += 1000000

    for file in listdir(PATH_USERS):
        if not file.endswith(".json"): continue
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

        for score in user[num_scores].values():
            bid = score["bid"]
            for file in listdir(PATH_BEATMAPSETS):
                if not file.endswith(".json"): continue
                with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                    mapset = json.load(f)

                if bid in mapset["beatmaps"].keys():
                    k = str(mapset["beatmaps"][bid])
                    num_scores[k] += 1
                    break

        for msid in user["beatmapsets"].keys():
            file = f"{msid}.json"
            if file in listdir(PATH_BEATMAPSETS):
                with open(file, "r", encoding="utf-8") as f:
                    mapset = json.load(f)

                for bmid, beatmap in user["beatmapsets"][msid].values():
                    if bmid in mapset["beatmaps"].keys():
                        k = str(beatmap["keys"])
                        beatmap_plays["keys"] += beatmap["total plays"]

        ranked_perc = { k:100*ranked_score[k]/max_ranked_score[k] for k in ["9", "10", "12", "14", "16", "18"]}
        total_perc = { k:100*total_score[k]/max_score[k] for k in ["9", "10", "12", "14", "16", "18"]}

        users_compact["users"][id]["name"] = name
        users_compact["users"][id]["last score"] = last_score
        users_compact["users"][id]["num scores"] = num_scores
        users_compact["users"][id]["ranked score"] = ranked_score
        users_compact["users"][id]["total score"] = total_score
        users_compact["users"][id]["ranked perc"] = ranked_perc
        users_compact["users"][id]["total perc"] = total_perc
        users_compact["users"][id]["beatmap plays"] = beatmap_plays
        users_compact["users"][id]["tracking"] = tracking
        users_compact["users"][id]["country"] = country

        users_compact["total"] += 1
        if tracking:
            users_compact["active"] += 1

    with open(output, "w", encoding="utf-8") as f:
        json.dump(users_compact, f)

if __name__ == "__main__":
    main()