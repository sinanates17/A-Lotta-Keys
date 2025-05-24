import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_USERS, PATH_BEATMAPSETS, PATH_DATA
from utils import Helper
from os import listdir
import json

def main():
    output = f"{PATH_DATA}/beatmaps_compact.json"
    beatmaps_compact = {}
    beatmaps_compact["beatmaps"] = {}
    beatmaps_compact["total"] = {}
    beatmaps_compact["ranked"] = {}
    beatmaps_compact["loved"] = {}

    unranked = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    ranked = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }
    loved = { k:0 for k in ["9", "10", "12", "14", "16", "18"] }

    for file in listdir(PATH_BEATMAPSETS):
        if not file.endswith(".json"): continue
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
            mapset = json.load(f)

        for bid, beatmap in mapset["beatmaps"].items():
            k = str(beatmap["keys"])
            if beatmap["status"] == 1:
                ranked[k] += 1
                status = "Ranked"
            elif beatmap["status"] == 4:
                loved[k] += 1
                status = "Loved"
            else:
                unranked[k] += 1
                status = "Unranked"

            name = f"{mapset["artist"]} - {mapset["title"] [{beatmap["version"]}]}"
            keys = beatmap["keys"]
            sr = beatmap["sr"]
            mapper = Helper.name_from_uid(beatmap["mapper id"])
            plays = beatmap["total plays"]
            passes = beatmap["total passes"]
            length = beatmap["length"]
            ln_perc = beatmap["ln"] / (beatmap["rice"] + beatmap["ln"])

            beatmaps_compact["beatmaps"][bid]["name"] = name
            beatmaps_compact["beatmaps"][bid]["keys"] = keys
            beatmaps_compact["beatmaps"][bid]["sr"] = sr
            beatmaps_compact["beatmaps"][bid]["mapper"] = mapper
            beatmaps_compact["beatmaps"][bid]["plays"] = plays
            beatmaps_compact["beatmaps"][bid]["passes"] = passes
            beatmaps_compact["beatmaps"][bid]["length"] = length
            beatmaps_compact["beatmaps"][bid]["ln perc"] = ln_perc
            beatmaps_compact["beatmaps"][bid]["status"] = status

    beatmaps_compact["unranked"] = unranked
    beatmaps_compact["ranked"] = ranked
    beatmaps_compact["loved"] = loved

    with open(output, "w", encoding="utf-8") as f:
        json.dump(beatmaps_compact, f)

if __name__ == "__main__":
    main()