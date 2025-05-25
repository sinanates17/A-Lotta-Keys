import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone
from utils import Helper
from config import PATH_SCORES, PATH_BEATMAPSETS, PATH_DATA
from os import listdir
import json

def main():
    helper = Helper()
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%d%H%M%S")
    output = f"scores_{now}.json"
    player_maps = {}
    cum_scores = { "timestamp": now }

    def _build_player_maps_update_beatmapset_jsons():
        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            path = f"{PATH_BEATMAPSETS}/{file}"
            lb_diffs = []
            if path.endswith(".json"):
                with open(path, "r") as f:
                    mapset = json.load(f)

                for id, diff in mapset['beatmaps'].items():
                    if diff['status'] in [4, 1]:
                        lb_diffs.append(id)

                for id in lb_diffs:
                    players = helper.beatmap_player_ids(id)
                    mapset['beatmaps'][id]['players'] = players
                    for player in players:
                        maps = player_maps.get(player, [])
                        maps.append(id)
                        player_maps[player] = maps

                with open(path, "w", encoding='utf-8') as f:
                    json.dump(mapset, f, ensure_ascii=False, indent=4)

    def _get_and_dump_scores():
        with open(f"{PATH_DATA}/beatmap_links.json", "r", encoding="utf-8") as f:
            beatmap_links = json.load(f)

        reqs = 0
        dels = []
        for player, maps in player_maps.items():
            if len(maps) < 25:
                dels.append(player)
                continue
            reqs += len(maps)

        for name in dels:
            del player_maps[name]

        i = 0
        for player, maps in player_maps.items():
            scores = helper.user_scores_many_beatmaps(user_id=player, beatmap_ids=maps)
            i += len(maps)
            print(f"{i} requests done of {reqs} | {i*100/reqs}%")
            for score in scores:
                score_dict = Helper.score_to_dict(score=score)
                score_dict["msid"] = beatmap_links[str(score_dict["bid"])] if str(score_dict["bid"]) in beatmap_links.keys() else None
                int_id = f"{score_dict['uid']}{score_dict['time']}"
                cum_scores[int_id] = score_dict

        with open(f"{PATH_SCORES}/{output}", "w", encoding='utf-8') as f:
            json.dump(cum_scores, f, ensure_ascii=False, indent=4)

    _build_player_maps_update_beatmapset_jsons()
    _get_and_dump_scores()

if __name__ == '__main__':
    main()