from datetime import datetime, timezone
from pathlib import Path
import sys
import json
from time import sleep

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.utils import Helper

def main():
    helper = Helper()
    timestamp_utc = datetime.now(timezone.utc)
    output_name = f"scores_9kp_recent_{timestamp_utc.strftime("%d-%m-%Y-%H-%M-%S")}.json"

    with open("data/user_ids.json", "r") as f:
        user_ids = json.load(f)[0:49]

    with open("data/user_ids_w_score_ids.json", "r") as f:
        user_ids_w_score_ids = json.load(f)

    with open("data/beatmap_ids_9kp_w_score_ids.json", "r") as f:
        beatmap_ids_w_score_ids = json.load(f)

    cum_recents = []

    for user_id in user_ids:
        sleep(2)
        recents_raw = helper.osu_api.user_scores(user_id=user_id, type='recent', mode='mania', limit=300)

        for recent in recents_raw:
            if recent.beatmap.cs <=8 or not recent.beatmap.mode == 'mania':
                del recent

        recents = [Helper.score_to_dict(score) for score in recents_raw]
        user_ids_w_score_ids[user_id] = list(set(user_ids_w_score_ids.get(user_id, []) + [recent["map id"] for recent in recents]))
        cum_recents += recents

        for score in recents:
            id = score["int id"]
            beatmap_ids_w_score_ids[id] = list(set(beatmap_ids_w_score_ids.get(id, []) + [score]))

    with open(f"data/raw/scores/{output_name}", "w") as f:
        json.dump(cum_recents, f)

    with open("data/beatmap_ids_9kp_w_score_ids.json", "w") as f:
        json.dump(beatmap_ids_w_score_ids, f)
    
if __name__ == "__main__":
    main()
