import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_BEATMAPSETS, PATH_DATA
from utils import Helper
from os import listdir
from datetime import datetime, timezone, timedelta
import json

def main():
    helper = Helper()
    now = datetime.now(timezone.utc)

    output = f"{PATH_DATA}/beatmaps_compact.json"
    beatmaps_compact = {}
    beatmaps_compact["unranked"] = {}
    beatmaps_compact["ranked"] = {}
    beatmaps_compact["loved"] = {}
    beatmaps_compact["beatmaps"] = {}

    unranked = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    ranked = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    loved = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }

    for file in listdir(PATH_BEATMAPSETS):
        if not file.endswith(".json"): continue
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
            mapset = json.load(f)

        for bid, beatmap in mapset["beatmaps"].items():
            updated = helper.datetime_from_timestamp(beatmap["updated"])

            k = str(int(beatmap["keys"]))
            sr = beatmap["sr"]
            passes = beatmap["total passes"]
            if k in ["11", "13", "15", "17"]: continue
            if sr > 15: continue
            if passes == 0: continue

            if beatmap["status"] == 1:
                ranked[k] += 1
                status = "Ranked"
            elif beatmap["status"] == 4:
                loved[k] += 1
                status = "Loved"
            else:
                unranked[k] += 1
                status = "Unranked"

            name = f"{mapset["artist"]} - {mapset["title"]} [{beatmap["version"]}]"
            keys = beatmap["keys"]
            mapper = Helper.name_from_uid(beatmap["mapper id"])
            plays = beatmap["total plays"]
            length = beatmap["length"]
            ln_perc = 100 * beatmap["ln"] / (beatmap["rice"] + beatmap["ln"]) if beatmap["rice"] + beatmap["ln"] != 0 else 0

            beatmaps_compact["beatmaps"][bid] = {}
            beatmaps_compact["beatmaps"][bid]["name"] = name
            beatmaps_compact["beatmaps"][bid]["keys"] = keys
            beatmaps_compact["beatmaps"][bid]["sr"] = sr
            
            beatmaps_compact["beatmaps"][bid]["mapper"] = mapper
            beatmaps_compact["beatmaps"][bid]["plays"] = plays
            beatmaps_compact["beatmaps"][bid]["passes"] = passes
            beatmaps_compact["beatmaps"][bid]["length"] = length
            beatmaps_compact["beatmaps"][bid]["ln perc"] = ln_perc
            beatmaps_compact["beatmaps"][bid]["status"] = status

            if ("sr HT" not in beatmaps_compact["beatmaps"][bid].keys() or 
                "sr DT" not in beatmaps_compact["beatmaps"][bid].keys() or
                updated > now - timedelta(days=2)):

                sr_HT = helper.sr_HT(int(bid))
                sr_DT = helper.sr_DT(int(bid))
                beatmaps_compact["beatmaps"][bid]["sr HT"] = sr_HT
                beatmaps_compact["beatmaps"][bid]["sr DT"] = sr_DT

    beatmaps_compact["unranked"] = unranked
    beatmaps_compact["ranked"] = ranked
    beatmaps_compact["loved"] = loved

    with open(output, "w", encoding="utf-8") as f:
        json.dump(beatmaps_compact, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()