"""
This is a manually-run script to retroactively calculate pp for existing scores
that don't have pp values.
"""

import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from config import PATH_SCORES
from os import listdir
import json

def main():
    links = Helper.load_beatmap_links()

    for file in listdir(PATH_SCORES):
        if not file.endswith(".json"): continue
        with open(f"{PATH_SCORES}/{file}", "r", encoding="utf-8") as f:
            scores = json.load(f)

        for sid, score in scores.items():
            if sid == "timestamp": 
                continue

            if score["pp"] is None:
                score["pp"] = Helper.calculate_pp(score)

            score["pp"] = round(score["pp"], 2)

            try:
                if score["msid"] is None:
                    score["msid"] = links[score["bid"]]
            except:
                pass
        
        with open(f"{PATH_SCORES}/{file}", "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()