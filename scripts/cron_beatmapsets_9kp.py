from datetime import datetime, timezone
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.utils import Helper

def main():
    timestamp_utc = datetime.now(timezone.utc)
    output_name = f"beatmapsets_9kp_{timestamp_utc.strftime("%d-%m-%Y-%H-%M-%S")}.json"

    helper = Helper()
    beatmapsets_9kp_raw = helper.cum_search_beatmapsets(query="keys>8", explicit_content="show", category="any")
    beatmap_ids_9kp = []
    beatmap_ids_9kp_rl = []

    for beatmapset in beatmapsets_9kp_raw:
        for beatmap in beatmapset.beatmaps:
            if beatmap.cs <= 8 or beatmap.mode.value != "mania":
                del beatmap
                continue

            beatmap_ids_9kp.append(beatmap.id)

            if beatmap.is_scoreable:
                beatmap_ids_9kp_rl.append(beatmap.id)

    beatmapsets_9kp_dict = { helper.beatmapset_to_dict(beatmapset)["id"]:helper.beatmapset_to_dict(beatmapset)
                                for beatmapset in beatmapsets_9kp_raw }
    
    with open(f"data/raw/beatmapsets/9kp/{output_name}", "w") as f:
        json.dump(beatmapsets_9kp_dict, f)

    with open("data/beatmap_ids_9kp.json", "w") as f:
        json.dump(beatmap_ids_9kp, f)

    with open("data/beatmap_ids_9kp_rl.json", "w") as f:
        json.dump(beatmap_ids_9kp_rl, f)

if __name__ == "__main__":
    main()

