import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone
from data.utils import Helper
from config import PATH_SCORES, PATH_BEATMAPSETS
from os import listdir
import json

def main():
    helper = Helper()
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%d%H%M%S")
    output = f"scores_{now}.json"
    player_maps = {}
    cum_scores = { "timestamp": now }

    def _build_player_maps_update_beatmapset_jsons(): #My goal is to make my code as unreadable as humanly possible
        for file in listdir(PATH_BEATMAPSETS)[0:3]:
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
        for player, maps in player_maps.items():
            scores = helper.user_scores_many_beatmaps(user_id=player, beatmap_ids=maps)
            for score in scores:
                score_dict = Helper.score_to_dict(score=score)
                int_id = f"{score_dict['uid']}{score_dict['time']}"
                cum_scores[int_id] = score_dict

        with open(f"{PATH_SCORES}/{output}", "w", encoding='utf-8') as f:
            json.dump(cum_scores, f, ensure_ascii=False, indent=4)

    _build_player_maps_update_beatmapset_jsons()
    _get_and_dump_scores()

if __name__ == '__main__':
    main()