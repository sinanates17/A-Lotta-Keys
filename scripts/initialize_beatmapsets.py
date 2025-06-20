import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from config import PATH_BEATMAPSETS, PATH_DATA
import json

def main():
    helper = Helper()
    mapsets = helper.cum_search_beatmapsets(
        query="keys>8", 
        explicit_content="show", 
        category="any")
    beatmap_links = {}

    for mapset in mapsets:
        msid = mapset.id
        dels = []
        for i, diff in enumerate(mapset.beatmaps):
            if diff.cs <= 8 or diff.mode.value != 'mania':
                dels.append(i)

        mapset.beatmaps = [beatmap for i, beatmap in enumerate(mapset.beatmaps) if i not in dels]
        
        mapset_dict = Helper.beatmapset_to_dict(mapset)
        msid = mapset_dict["id"]
        for bmid in mapset_dict["beatmaps"].keys():
             beatmap_links[bmid] = msid

        filename = f"{mapset.id}.json".translate(str.maketrans("", "", "/\\"))
        with open(f"{PATH_BEATMAPSETS}/{filename}", "w", encoding='utf-8') as f:
            json.dump(mapset_dict, f, ensure_ascii=False, indent=4)

    with open(f"{PATH_DATA}/beatmap_links.json", "w", encoding='utf-8') as f:
            json.dump(beatmap_links, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()