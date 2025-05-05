"""
WARNING: This script makes a LOT of API requests over a LONG period, and is only meant to be used
         on a one-off basis.

Gets and preprocesses every available score for every userid in root/data/user_ids.json on every 9K+ map with a leaderboard
"""

from datetime import datetime, timezone
from pathlib import Path
import sys
import json
from time import sleep

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.utils import Helper

def main():
    with open("data/user_ids.json", "r") as f:
        user_ids = json.load(f)[0:6]

    with open("data/beatmap_ids_9kp_rl.json", "r") as f:
        beatmap_ids = json.load(f)[0:6]

    helper = Helper()
    scores_dict = {}
    user_ids_w_score_ids_dict = {id:[] for id in user_ids}
    beatmap_ids_w_score_ids_dict = { id:[] for id in beatmap_ids}
    beatmap_ids_w_user_ids_dict = helper.user_ids_per_beatmap(beatmap_ids=beatmap_ids)

    for beatmap_id, users in beatmap_ids_w_user_ids_dict.items():
        for i, user in enumerate(users):
            print(f"{beatmap_id} | {i+1} of {len(users)}")
            scores_raw = helper.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user)
            scores_dict = scores_dict | {helper.score_to_dict(score)["internal id"]:helper.score_to_dict(score) for score in scores_raw}
            user_ids_w_score_ids_dict[user] = [score["internal id"] for score in list(scores_dict.values())]

            for score in scores_dict.values():
                beatmap_ids_w_score_ids_dict[score["beatmap id"]].append(score["internal id"])

    #for user_id in user_ids:
    #    scores_raw = helper.user_scores_many_beatmaps(user_id=user_id, beatmap_ids=beatmap_ids)
    #    scores_dict = scores_dict | {helper.score_to_dict(score)["internal id"]:helper.score_to_dict(score) for score in scores_raw}
    #    user_ids_w_score_ids_dict[user_id] = [score["internal id"] for score in list(scores_dict.values())]

    #    for score in scores_dict.values():
    #        beatmap_ids_w_score_ids_dict[score["beatmap id"]].append(score["internal id"])

    #Update existing jsons with any new data
    with open("data/raw/scores/scores_9kp.json", "r") as f:
        scores_dict_old = json.load(f)

    scores_dict = scores_dict | scores_dict_old

    with open("data/raw/scores/scores_9kp.json", "w") as f:
        json.dump(scores_dict, f)

    #data/user_ids_w_score_ids.json
    with open("data/user_ids_w_score_ids.json", "r") as f:
        user_ids_w_score_ids_dict_old = json.load(f)

    for key in user_ids_w_score_ids_dict.keys() | user_ids_w_score_ids_dict_old.keys():
        user_ids_w_score_ids_dict[key] = list(set(user_ids_w_score_ids_dict.get(key, []) + 
                                                  user_ids_w_score_ids_dict_old.get(key, [])))
        
    with open("data/user_ids_w_score_ids.json", "w") as f:
        json.dump(user_ids_w_score_ids_dict, f)
  
    #data/beatmap_ids_9kp_w_score_ids.json
    with open("data/beatmap_ids_9kp_w_score_ids.json", "r") as f:
        beatmap_ids_w_score_ids_dict_old = json.load(f)

    for key in beatmap_ids_w_score_ids_dict.keys() | beatmap_ids_w_score_ids_dict_old.keys():
        beatmap_ids_w_score_ids_dict[key] = list(set(beatmap_ids_w_score_ids_dict.get(key, []) +
                                                     beatmap_ids_w_score_ids_dict_old.get(key, [])))
        
    with open("data/beatmap_ids_9kp_w_score_ids.json", "w") as f:
        json.dump(beatmap_ids_w_score_ids_dict, f)

if __name__ == "__main__":
    main()

