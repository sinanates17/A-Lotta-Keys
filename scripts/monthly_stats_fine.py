import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime
from config import PATH_DATA, PATH_USERS, PATH_BEATMAPSETS
from os import listdir
import json

def main():
    def _latest_cumstats_key():
        latest_dates = []
        for key, stats in cum_stats.items():
            if stats["legacy"]: continue
            date = datetime.strptime(key, "%y%m%d%H%M%S")

            latest_dates.append(date)

        latest_dates.sort()
        latest_dates.reverse()

        if latest_dates:
            latest_date = latest_dates[1].strftime("%y%m%d%H%M%S")

        return latest_date
    
    def _stats_users():
        for file in listdir(PATH_USERS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_USERS}/{file}", "r", encoding='utf-8') as f:
                user = json.load(f)
            uid = user["id"]

            no_scores = 0
            for score in user["scores"]:
                time = datetime.strptime(score["time"], "%y%m%d%H%M%S")
                if time > latest_date:
                    no_scores += 1

            plays = []
            for key, count in user["total beatmap plays"].items():
                time = datetime.strptime(key, "%y%m%d%H%M%S")
                if time > latest_date:
                    plays.append(count)
            if plays:
                plays = max(plays) - min(plays)
            else:
                plays = 0

            tracker["top mappers"].append([uid, plays])
            tracker["top players"].append([uid, no_scores])

        tracker["top mappers"].sort(lambda x: x[1])
        tracker["top players"].sort(lambda x: x[1])
        tracker["top mappers"] = tracker["top mappers"][0:50]
        tracker["top players"] = tracker["top players"][0:50]

    def _stats_beatmaps():
        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            with open(f"{PATH_BEATMAPSETS}/{file}", "r", encoding='utf-8') as f:
                mapset = json.load(f)
            msid = mapset["id"]

            for bmid, beatmap in mapset["beatmaps"].items():
                plays = []
                for key, count in beatmap["plays over time"].items():
                    time = datetime.strptime(key, "%y%m%d%H%M%S")
                    if time > latest_date:
                        plays.append(count)
                if plays:
                    plays = max(plays) - min(plays)
                else:
                    plays = 0
                
                tracker["top maps"].append([msid, bmid, plays])

        tracker["top maps"].sort(lambda x: x[2])
        tracker["top maps"]= tracker["top maps"][0:50]

    with open(f"{PATH_DATA}/{output}", "r", encoding='utf-8') as f:
        cum_stats = json.load(f)

    output = "cumulative_stats_timeline.json"
    latest_key = _latest_cumstats_key()
    if not latest_key: return
    latest_date = datetime.strptime(latest_key, "%y%m%d%H%M%S")
    tracker = {
        "top mappers": [], # [uid, plays]
        "top players": [], # [uid, plays]
        "top maps": [] }   # sid : [bmid, plays]
    
    _stats_users()
    _stats_beatmaps()

    cum_stats[latest_key]["top mappers"] = tracker["top mappers"]
    cum_stats[latest_key]["top players"] = tracker["top players"]
    cum_stats[latest_key]["top maps"] = tracker["top maps"]

    with open(f"{PATH_DATA}/{output}", "w", encoding='utf-8') as f:
        json.dump(cum_stats, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()