"""
This is a manually-run script to retroactively extract a pp history for every user.
"""

import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import Helper
from config import PATH_USERS, PATH_BEATMAPSETS
from os import listdir
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import json
from time import time
from multiprocessing import Pool
from functools import partial

def _process_user_file(file, bid_keys, states, keys):
    if not file.endswith(".json"): return
    with open(f"{PATH_USERS}/{file}", "r", encoding="utf-8") as f:
        user = json.load(f)

    pp_history = {}

    if user["scores"] == {}: return
    subscores = [score for score in user["scores"].values() if score["pb"]]
    bids = {score["bid"] for score in user["scores"].values()}
    cutoff = datetime.now(timezone.utc)
    interval = relativedelta(days=1)
    key = (lambda x: 
                datetime.strptime(x["time"], "%y%m%d%H%M%S")
                .replace(tzinfo=timezone.utc)
                < cutoff)

    while True:
        n_old = len(subscores)
        subscores = list(filter(key, subscores))
        n_new = len(subscores)

        if n_new == 0: 
            break
        if n_new == n_old:
            cutoff -= interval
            continue

        pps = { state: { k:0 for k in keys } for state in states }
        pp_lists = { state: { k:[] for k in keys } for state in states }

        for bid in bids:
            subsubscores = list(filter(lambda x: x["bid"] == bid, subscores))
            if len(subsubscores) == 0: continue

            bid_pps = [score["pp"] for score in subsubscores]

            pp = max(bid_pps)
            bid = str(bid)
            k = bid_keys[bid][0]
            status = bid_keys[bid][1]

            key_groups = [k, "9+"]
            if k != "9":
                key_groups.append("10+")

            if k != "9" or k != "10":
                key_groups.append("12+")

            status_groups = ["RLU"]
            if status == 1:
                status_groups += ["R", "RL"]

            elif status == 4:
                status_groups += ["L", "RL"]

            else:
                status_groups += ["U"]

            for status_group in status_groups:
                for key_group in key_groups:
                    pp_lists[status_group][key_group].append(pp)

        timestamp = cutoff.strftime("%y%m%d%H%M%S")
        for state in states:
            for k in keys:
                pps[state][k] = Helper.calculate_profile_pp(pp_lists[state][k])

        pp_history[timestamp] = pps
        cutoff -= interval

    user["pp history"] = pp_history

    with open(f"{PATH_USERS}/{file}", "w", encoding='utf-8') as f:
        json.dump(user, f, ensure_ascii=False, indent=4)

def main():
    start = time()
    states = ["R", "L", "U", "RL", "RLU"]
    keys = ["9", "10", "12", "14", "16", "18", "9+", "10+", "12+"]
    bid_keys = {}
    for file in listdir(PATH_BEATMAPSETS):
        if not file.endswith(".json"): continue
        with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding="utf-8") as f:
            mapset = json.load(f)

        for bid, beatmap in mapset["beatmaps"].items():
            bid_keys |= {bid: (str(int(beatmap["keys"])), beatmap["status"])}
        
    parfunct = partial(_process_user_file, bid_keys=bid_keys, states=states, keys=keys)

    files = listdir(PATH_USERS)

    with Pool() as pool:
        pool.map(parfunct, files)

    end = time()
    print(round(end - start, 2))

if __name__ == "__main__":
    main()