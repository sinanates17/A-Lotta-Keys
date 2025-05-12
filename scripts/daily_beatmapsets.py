import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from data.utils import Helper
from config import PATH_SCORES, PATH_BEATMAPSETS
from os import listdir
import json

def main():
    def _old_version(id: int) -> dict:
        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                result = json.load(f)
            
            if result["id"] == id:
                return result
        
        return None

    def _update_mapsets():
        for mapset in mapsets:
            dels = []
            for i, diff in enumerate(mapset.beatmaps):
                if diff.cs <= 8 or diff.mode.value != 'mania':
                    dels.append(i)

            mapset.beatmaps = [beatmap for i, beatmap in enumerate(mapset.beatmaps) if i not in dels]
            
            mapset_dict = Helper.beatmapset_to_dict(mapset)
            mapset_dict_old = _old_version(mapset.id)

            if mapset_dict_old:
                diffs = list(mapset_dict["beatmaps"].keys())
                diffs_old = list(mapset_dict_old["beatmaps"].keys())

                #new_diffs = [id for id in diffs if id not in diffs_old]
                same_diffs = [id for id in diffs if id in diffs_old]
                del_diffs = [id for id in diffs_old if id not in diffs]

                for bid, diff in mapset_dict_old["beatmaps"].items():
                    if bid in same_diffs:
                        mapset_dict["beatmaps"][bid]["scores"] = diff["scores"]
                        mapset_dict["beatmaps"][bid]["players"] = diff["players"]
                        mapset_dict["beatmaps"][bid]["play history"] = diff["play history"]
                        mapset_dict["beatmaps"][bid]["pass history"] = diff["pass history"]
                        mapset_dict["beatmaps"][bid]["play history"][now] = mapset_dict["total plays"]
                        mapset_dict["beatmaps"][bid]["pass history"][now] = mapset_dict["total passes"]

                    if bid in del_diffs:
                        diff["deleted"] = now
                        mapset_dict["beatmaps"][bid] = diff

            filename = f"{mapset_dict_old["artist"]} - {mapset_dict_old["title"]}.json".translate(str.maketrans("", "", "/\\"))
            with open(f"{PATH_BEATMAPSETS}/{filename}", "w", encoding='utf-8') as f:
                json.dump(mapset_dict, f, ensure_ascii=False, indent=4)

    def _update_scores():
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=2)
        now = now.strftime("%y%m%d%H%M%S")
        cutoff = cutoff.strftime("%y%m%d%H%M%S")
        bids_scores = {}

        for file in listdir(PATH_SCORES):
            if not file.endswith(".json"): continue
            with open(f"{PATH_SCORES}/{file}", "r", encoding='utf-8') as f:
                scores = json.load(f)

            if int(scores["timestamp"]) > int(cutoff):
                for sid, score in scores.items():
                    if sid == "timestamp": continue

                    bid = score["bid"]
                    bid_scores = bids_scores.get(bid, {})
                    bid_scores[sid] = score
                    bids_scores[bid] = bid_scores

        for bid, scores in bids_scores.items():
            for file in listdir(PATH_BEATMAPSETS):
                if not file.endswith(".json"): continue
                with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                    mapset = json.load(f)
                
                if bid in mapset["beatmaps"].keys():
                    mapset["beatmaps"][bid]["scores"] |= scores

                    with open(f"{PATH_BEATMAPSETS}/{file}", "w", encoding='utf-8') as f:
                        json.dump(mapset, f, ensure_ascii=False, indent=4)

                    break

    helper = Helper()
    mapsets = helper.cum_search_beatmapsets(
        query="keys>8", 
        explicit_content="show", 
        category="any")
    now = datetime.now(timezone.utc)
    now = now.strftime("%y%m%dH%M%S")
    
    _update_mapsets()
    _update_scores()

if __name__ == '__main__':
    main()