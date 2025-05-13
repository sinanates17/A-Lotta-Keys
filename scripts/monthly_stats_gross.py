import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from data.utils import Helper
from config import PATH_DATA
from os import listdir
import pandas as pd
import json

def main():
    def _generate(mapsets):
        cum_stats = {
            k: {"plays":0, 
                "passes":0, 
                "diffs":0, 
                "drain" :0, 
                "circles":0, 
                "sliders":0, 
                "sr": []} 
                for k in [4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18]}
        cum_stats["top mappers"] = None
        cum_stats["top beatmaps"] = None
        cum_stats["top players"] = None
        cum_stats["new beatmaps"] = {}

        for mapset in mapsets:
            msid = mapset.id
            for beatmap in mapset.beatmaps:
                if beatmap.mode.value != "mania" or beatmap.cs < 4 or not beatmap.is_scoreable: continue
                bid = beatmap.id
                k = beatmap.cs
                plays = beatmap.playcount
                passes = beatmap.passcount
                drain = beatmap.total_length
                circles = beatmap.count_circles
                sliders = beatmap.count_sliders
                sr = beatmap.difficulty_rating

                cum_stats[k]["plays"] += plays
                cum_stats[k]["passes"] += passes
                cum_stats[k]["diffs"] += 1
                cum_stats[k]["drain"] += drain
                cum_stats[k]["circles"] += circles
                cum_stats[k]["sliders"] += sliders
                cum_stats[k]["sr"].append(sr)

                if k >= 9:
                    bids = cum_stats["new beatmaps"].get(msid, [])
                    bids.append(bid)
                    cum_stats["new beatmaps"][msid] = bids
        
        return cum_stats
    
    helper = Helper()
    output = "cumulative_stats_timeline.json"
    now = datetime.now(timezone.utc)
    str_now = now.strftime("%y%m%d%H%M%S")
    previous_date = None

    if output in listdir(PATH_DATA):
        with open(output, "r", encoding='utf-8') as f:
            cum_stats_timeline = json.load(f"{PATH_DATA}/{output}")
        
        previous_date = list(cum_stats_timeline.keys())[-1].strptime("%y%m%d%H%M%S")
        mapsets = helper.cum_search_beatmapsets(
            start_date=previous_date,
            end_date=now,
            query="keys>3",
            explicit_content="show")
        
        stats = _generate(mapsets=mapsets)
        cum_stats_timeline[str_now] = stats
        
    else:
        cum_stats_timeline = {}
        mapsets = helper.cum_search_beatmapsets(
            query="keys>3",
            explicit_content="show")
        temp_timeline = []
        end = now
        start = now - relativedelta(months=1, day=1) #First day of last month
        birth = datetime(tzinfo=timezone.utc, year=2013, month=1, day=1)
        
        while start > birth:
            str_time = end.strftime("%y%m%d%H%M%S")
            target_mapsets = [mapset for mapset in mapsets if mapset.ranked_date > start and mapset.ranked_date < end]
            stats =  _generate(target_mapsets)
            temp_timeline.append((str_time, stats))
            end = start
            start = start - relativedelta(months=1)

        for t, stats in reversed(temp_timeline):
            cum_stats_timeline[t] = stats

    with open(f"{PATH_DATA}/{output}", "w", encoding = 'utf-8') as f:
        json.dump(cum_stats_timeline, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()