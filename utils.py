from ossapi import Ossapi, Beatmapset, Beatmap, Score, User, Statistics
from config import OSU_API_ID, OSU_API_SECRET, REQUEST_INTERVAL, PATH_USERS, PATH_DATA, PATH_BEATMAPSETS, PATH_PYTHON, PATH_ROOT
from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from time import sleep
from os import listdir
from osu_db_tools.score import Score as ScoreDB
import json
import numpy as np
import requests
import subprocess

class Helper:

    PP_WEIGHTS = np.array([.95 ** n for n in range(200)])
    DOTNET_EPOCH = datetime(1, 1, 1, tzinfo=timezone.utc)
    MOD_BITFLAGS = {
        1 << 0: "NF",
        1 << 1: "EZ",
        1 << 3: "HD",
        1 << 4: "HR",
        1 << 5: "SD",
        1 << 6: "DT",
        1 << 8: "HT",
        1 << 9: "NC",
        1 << 10: "FL",
        1 << 14: "PF",
        1 << 20: "FI",
        1 << 21: "RD",
        1 << 29: "V2",
        1 << 30: "MR"
    }

    def __init__(self, prefix="[Helper] "):
        self.prefix = prefix
        self.osu_api = Ossapi(client_id=OSU_API_ID, client_secret=OSU_API_SECRET)

    @staticmethod
    def beatmapset_to_dict(beatmapset: Beatmapset):
        beatmapset_dict = {
            'id': beatmapset.id,
            'title': beatmapset.title,
            'artist': beatmapset.artist,
            'titleu': beatmapset.title_unicode,
            'artistu': beatmapset.artist_unicode,
            'favs': beatmapset.favourite_count,
            'desc': beatmapset.description,
            'source': beatmapset.source,
            'tags': beatmapset.tags,
            'host id': beatmapset.user_id,
            'submitted': beatmapset.submitted_date.strftime("%y%m%d%H%M%S"),
            'ranked' : beatmapset.ranked_date.strftime("%y%m%d%H%M%S") if isinstance(beatmapset.ranked_date, datetime) else 'unranked',
            'beatmaps': {beatmap.id:Helper.beatmap_to_dict(beatmap) for beatmap in beatmapset.beatmaps},
        }

        return beatmapset_dict
    
    @staticmethod
    def beatmap_to_dict(beatmap: Beatmap):
        now = datetime.now(timezone.utc)
        now = now.strftime("%y%m%d%H%M%S")
        beatmap_dict = {
            'version': beatmap.version,
            'sr': beatmap.difficulty_rating,
            'keys': beatmap.cs,
            'mapper id': beatmap.owner.id if beatmap.owner is not None else beatmap.user_id,
            'status': beatmap.status.value, #G-2|W-1|P0|R1|A2|Q3|L4
            'updated': beatmap.last_updated.strftime("%y%m%d%H%M%S"),
            'deleted': None,
            'url': beatmap.url,
            'length': beatmap.total_length,
            'rice': beatmap.count_circles,
            'ln': beatmap.count_sliders,
            'players': [],
            'total plays': beatmap.playcount,
            'total passes': beatmap.passcount,
            'play history': {now:beatmap.playcount},
            'pass history': {now:beatmap.passcount},
            'scores': {}
        }

        return beatmap_dict
    
    @staticmethod
    def score_to_dict_db(score: ScoreDB, uid, bid, msid) -> dict:
        def _mods_from_int(val) -> list:
            mods = ["CL"]
            mods += [mod for bit, mod in Helper.MOD_BITFLAGS.items() if val & bit]
            return mods
        
        def _time_from_winticks(ts) -> str:
            score_datetime = Helper.DOTNET_EPOCH + timedelta(seconds=ts / 10_000_000)
            score_timestamp = score_datetime.strftime("%y%m%d%H%M%S")
            return score_timestamp

        c320 = score.num_gekis
        c300 = score.num_300s
        c200 = score.num_katus
        c100 = score.num_100s
        c50 = score.num_50s
        c0 = score.num_misses
        t = c320 + c300 + c200 + c100 + c50 + c0

        acc = ((c320 + c300)*300 + c200*200 + c100*100 + c50*50) / (t * 300)

        grade = "F"
        match acc:
            case x if x == 1:
                grade = 'X'
            case x if x >=.95:
                grade = 'S'
            case x if x >= .9:
                grade = 'A'
            case x if x >= .8:
                grade = 'B'
            case x if x >= .7:
                grade = 'C'
            case x if x < .7:
                grade = 'D'

        score_dict = {
            'uid': uid,
            'bid': bid,
            'msid': msid,
            'time': _time_from_winticks(score.timestamp),
            'mods': _mods_from_int(score.mods),
            'combo': score.max_combo,
            'passed': True,
            'pp': 0,
            'pb': None,
            'top': None,
            'old': None,
            'acc': acc,
            'grade': grade,
            'score': score.replay_score,
            '320': c320,
            '300': c300,
            '200': c200,
            '100': c100,
            '50': c50,
            '0': c0
        }

        if score_dict["pp"] == 0:
            try:
                score_dict["pp"] = Helper.calculate_pp(score_dict)
            except:
                pass

        return score_dict

    @staticmethod
    def score_to_dict(score: Score):

        def _calc_judgements(stats: Statistics) -> tuple[float, str]:
            c320 = stats.perfect if score.statistics.perfect is not None else 0
            c300 = stats.great if score.statistics.great is not None else 0
            c200 = stats.good if score.statistics.good is not None else 0
            c100 = stats.ok if score.statistics.ok is not None else 0
            c50 = stats.meh if score.statistics.meh is not None else 0
            c0 = stats.miss if score.statistics.miss is not None else 0
            t = c320 + c300 + c200 + c100 + c50 + c0

            acc = ((c320 + c300)*300 + c200*200 + c100*100 + c50*50) / (t * 300)

            if not score.passed:
                return acc, 'F'

            match acc:
                case x if x == 1:
                    return acc, 'X'
                case x if x >=.95:
                    return acc, 'S'
                case x if x >= .9:
                    return acc, 'A'
                case x if x >= .8:
                    return acc, 'B'
                case x if x >= .7:
                    return acc, 'C'
                case x if x < .7:
                    return acc, 'D'

        score_dict = {
            'uid': score.user_id,
            'bid': int(score.beatmap_id) if isinstance(score.beatmap_id, str) or isinstance(score.beatmap_id, int) else int(score.beatmap.id),
            'msid': None,
            'time': score.ended_at.strftime("%y%m%d%H%M%S"),
            'mods': [mod.acronym for mod in score.mods],
            'combo': score.max_combo,
            'passed': score.passed,
            'pp': score.pp,
            'pb': None,
            'top': None,
            'old': None,
            'acc': _calc_judgements(score.statistics)[0],
            'grade': _calc_judgements(score.statistics)[1],
            'score': score.legacy_total_score if score.legacy_total_score != 0 else score.classic_total_score,
            '320': score.statistics.perfect if score.statistics.perfect is not None else 0,
            '300': score.statistics.great if score.statistics.great is not None else 0,
            '200': score.statistics.good if score.statistics.good is not None else 0,
            '100': score.statistics.ok if score.statistics.ok is not None else 0,
            '50': score.statistics.meh if score.statistics.meh is not None else 0,
            '0': score.statistics.miss if score.statistics.miss is not None else 0
        }

        if score.pp is None:
            try:
                score_dict["pp"] = Helper.calculate_pp(score_dict)
            finally:
                pass

        return score_dict
    
    @staticmethod
    def user_to_dict(user: User):
        user_dict = {
            'id': user.id,
            'name': user.username,
            'avatar url': user.avatar_url,
            'days ago': 0,
            'country': user.country.name,
            'tracking': True,
            'beatmapsets': {},
            'beatmap plays history': {},
            'scores': {},
        }

        return user_dict
    
    @staticmethod
    def name_from_uid(uid: int):
        file = f"{uid}.json"
        if file in listdir(PATH_USERS):
            with open(f"{PATH_USERS}/{file}", "r", encoding="utf8") as f:
                user = json.load(f)
            name = user["name"]
            return name
        return None

    @staticmethod
    def calculate_pp(score_dict: dict, sr=None):
        c320 = score_dict["320"]
        c300 = score_dict["300"]
        c200 = score_dict["200"]
        c100 = score_dict["100"]
        c50 = score_dict["50"]
        c0 = score_dict["0"]
        total_hits = c320 + c300 + c200 + c100 + c50 + c0
        acc = (320 * c320 + 300 * c300 + 200 * c200 + 100 * c100 + 50 * c50) / (320 * total_hits)

        try:
            if sr is None:
                sr = Helper.get_sr_of_beatmap(score_dict["bid"], mods=score_dict["mods"])

            base_mult = 8
            sr_mult = max(.05, (sr - .15)) ** 2.2
            acc_mult = max(0, (5 * acc - 4))
            length_mult = 1 + .1 * min(1, (total_hits / 1500))

            pp = base_mult * sr_mult * acc_mult * length_mult

            pp = round(pp, 2)

        except:
            pp = 0

        return pp
    
    @staticmethod
    def calculate_profile_pp(pps: list):
        N = len(pps)

        bonus_pp = 416.6667 * (1 - .995 ** min(N, 1000))

        pps.sort(reverse=True)

        if N > 200:
            pps = pps[0:200]

        if N < 200:
            pps += [0] * (200 - N)

        pps = np.array(pps)

        total_pp = float(np.dot(pps, Helper.PP_WEIGHTS))

        total_pp += bonus_pp

        total_pp = round(total_pp, 2)

        return total_pp

    @staticmethod
    def get_sr_of_beatmap(bid, mods):

        bid = str(bid)
        compact = Helper.load_beatmaps_compact()
        
        beatmap = compact["beatmaps"][bid]

        if "HT" in mods:
            sr = beatmap["sr HT"]
        elif "DT" in mods or "NC" in mods:
            sr = beatmap["sr HT"]
        else:
            sr = beatmap["sr"]

        return sr

    @staticmethod
    def load_beatmap_links():
        with open(f"{PATH_DATA}/beatmap_links.json", "r", encoding="utf-8") as f:
            links = json.load(f)

        return links
    
    @staticmethod
    def load_beatmap_hashes():
        try:
            with open(f"{PATH_DATA}/beatmap_hashes.json", "r", encoding="utf-8") as f:
                links = json.load(f)

            return links
        except:
            return {}
    
    @staticmethod
    def load_beatmaps_compact():
        with open(f"{PATH_DATA}/beatmaps_compact.json", "r", encoding="utf-8") as f:
            compact = json.load(f)

        return compact

    @staticmethod
    def load_mapset(msid):
        with open(f"{PATH_BEATMAPSETS}/{msid}.json", "r", encoding="utf-8") as f:
            mapset = json.load(f)

        return mapset

    @staticmethod
    def load_user(uid):
        with open(f"{PATH_USERS}/{uid}.json") as f:
            user = json.load(f)

        return user

    @staticmethod
    def datetime_from_timestamp(ts):
        dt = datetime.strptime(ts, "%y%m%d%H%M%S")
        dt.replace(tzinfo=timezone.utc)

        return dt

    @staticmethod
    def process_user_scores(uid):
        try:
            user = Helper.load_user(uid)
        except:
            return
        
        beatmaps_compact = Helper.load_beatmaps_compact()

        scores = user["scores"]

        if scores == {}: return
        
        bids = {score["bid"] for score in scores.values()}
        bids = {bid: [score for score in scores.items() if score[1]["bid"] == bid] for bid in bids}

        updated_scores = {}

        for bid, subscores in bids.items():
            subscores.sort(key=lambda x: int(x[1]["time"]))

            try:
                updated = beatmaps_compact["beatmaps"][str(bid)]["date"]
                updated = datetime.strptime(updated, "%y%m%d%H%M%S")

            except:
                updated = datetime.now()

            record = 0
            for score in subscores:
                time = datetime.strptime(score[1]["time"], "%y%m%d%H%M%S")
                
                if time > updated:
                    score[1]["old"] = False
                else:
                    score[1]["old"] = True

                if score[1]["score"] > record:
                    score[1]["pb"] = True
                    record = score[1]["score"]
                    sid_top = score[0]

                else:
                    score[1]["pb"] = False

            for score in subscores:
                if score[0] == sid_top:
                    score[1]["top"] = True

                else:
                    score[1]["top"] = False

                updated_scores |= dict([score])

        user["scores"] = updated_scores

        with open(f"{PATH_USERS}/{uid}.json", "w", encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=4)

    def cum_search_beatmapsets(self, start_date=None, end_date=None, **kwargs) -> list[Ossapi.beatmapset]:
        sleep(REQUEST_INTERVAL)
        result = self.osu_api.search_beatmapsets(**kwargs)
        total = result.beatmapsets
        page = 1
        print(f'Page {page}') #Temporary until I implement a logger

        while result.cursor is not None:
            sleep(REQUEST_INTERVAL)
            page += 1
            print(f'Page {page}') #Temporary until I implement a logger
            result = self.osu_api.search_beatmapsets(**kwargs, cursor=result.cursor)

            for beatmapset in result.beatmapsets:
                beatmapset.last_updated.replace(tzinfo=timezone.utc)
                if beatmapset.ranked_date is not None:
                    beatmapset.ranked_date.replace(tzinfo=timezone.utc)
                if isinstance(end_date, datetime):
                    if beatmapset.ranked.value in [1,4]:
                        if beatmapset.ranked_date > end_date: continue
                    else:
                        if beatmapset.last_updated > end_date: continue

                if isinstance(start_date, datetime):
                    if beatmapset.ranked.value in [1,4]:
                        if beatmapset.ranked_date < start_date: 
                            result.cursor = None; break
                    else:
                        if beatmapset.last_updated < start_date: 
                            result.cursor = None; break

                total.append(beatmapset)


        return total
    
    def recent_beatmap_ids(self, limit=10) -> list[Ossapi.beatmapset]:
        sleep(REQUEST_INTERVAL)
        mapsets = self.osu_api.search_beatmapsets(
            query="keys>8", 
            explicit_content="show").beatmapsets[0:limit]
        
        bids = []

        for mapset in mapsets:
            for diff in mapset.beatmaps:
                if diff.cs >= 8 and diff.mode.value == 'mania':
                    bids.append(diff.id)

        return bids

    def user_scores_many_beatmaps(self, user_id: int, beatmap_ids: list[int]) -> list[Score]:
        scores = []
        length = len(beatmap_ids)

        for i, beatmap_id in enumerate(beatmap_ids):
            sleep(REQUEST_INTERVAL)
            print(f"Request {i+1} of {length}") #Temporary until I implement a logger
            try:
                results = self.osu_api.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user_id)
                for result in results: #This is a monkey patch since beatmap_user_scores() doesnt include a beatmap or beatmap id in the returned scores.
                    result.beatmap_id = beatmap_id
                scores += results
            finally:
                continue

        return scores
    
    def user_ids_per_beatmap(self, beatmap_ids: list[int]) -> dict[int:list[int]]:
        beatmap_ids_w_user_ids = { id:[] for id in beatmap_ids}

        for i, beatmap_id in enumerate(beatmap_ids):
            sleep(REQUEST_INTERVAL)
            beatmap_scores = self.osu_api.beatmap_scores(beatmap_id=beatmap_id, limit=100).scores
            beatmap_ids_w_user_ids[beatmap_id] = [score.user_id for score in beatmap_scores]
            print(f"Beatmap {i+1} of {len(beatmap_ids)} | {len(beatmap_scores)} users")

        return beatmap_ids_w_user_ids
    
    def beatmap_player_ids(self, beatmap_id: int) -> list[int]:
        sleep(REQUEST_INTERVAL)
        scores = self.osu_api.beatmap_scores(beatmap_id=beatmap_id, limit=100).scores
        ids = [score.user_id for score in scores]
        return ids
    
    def beatmap_user_scores(self, beatmap_id: int, user_id: int, **kwargs) -> list[Score]:
        sleep(REQUEST_INTERVAL)
        print(beatmap_id, user_id)
        scores = self.osu_api.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user_id, **kwargs)

        for score in scores: #This is a monkey patch since beatmap_user_scores() doesnt include a beatmap or beatmap id in the returned scores.
            score.beatmap_id = beatmap_id
        
        return scores
    
    def users(self, user_ids: list[int]) -> list[User]:

        size = len(user_ids)
        sublists = [user_ids[i*50:(i+1)*50] for i in range(size//50)]
        sublists.append(user_ids[50*(size//50):size])

        users = []
        for sublist in sublists:
            sleep(REQUEST_INTERVAL * 5)
            users += self.osu_api.users(user_ids=sublist)
        return users
    
    def user_scores_recent(self, user_id: int) -> list[Score]:
        sleep(REQUEST_INTERVAL)
        scores = self.osu_api.user_scores(user_id=user_id, type="recent", limit=500)
        return scores
    
    def sr_DT(self, beatmap_id):
        sleep(REQUEST_INTERVAL)
        try:
            attr = self.osu_api.beatmap_attributes(beatmap_id=beatmap_id, mods="DT")
            sr = attr.attributes.star_rating
        except:
            sr = 0
        return sr
    
    def sr_HT(self, beatmap_id):
        sleep(REQUEST_INTERVAL)
        try:
            attr = self.osu_api.beatmap_attributes(beatmap_id=beatmap_id, mods="HT")
            sr = attr.attributes.star_rating
        except:
            sr = 0
        return sr
    
    def recent_beatmaps(self):
        """
        Manually request the beatmapsets/search endpoint because ossapi doesn't
        work with the "updated_desc" sort option. This is specifically for the
        Discord bot's mapfeed loop.
        """

        token_url = "https://osu.ppy.sh/oauth/token"
        data = {
            "client_id": OSU_API_ID,
            "client_secret": OSU_API_SECRET,
            "grant_type": "client_credentials",
            "scope": "public"
        }

        resp = requests.post(token_url, json=data)
        resp.raise_for_status()
        token_info = resp.json()
        access_token = token_info["access_token"]

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        url = "https://osu.ppy.sh/api/v2/beatmapsets/search?e=&c=&g=&l=&m=&nsfw=&played=&q=keys%3E8&r=&sort=updated_desc&s=any"
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        resp = resp.json()
        resp = resp["beatmapsets"]

        return resp[0:5]

    def initialize_user(self, uid):
        filename = f"{uid}.json"
        output = f"{PATH_USERS}/{filename}"

        if filename not in listdir(PATH_USERS):
            helper = Helper()
            sleep(REQUEST_INTERVAL)
            user = helper.osu_api.user(uid)
            user_dict = Helper.user_to_dict(user)
        else:
            user_dict = Helper.load_user(uid)

        beatmaps = Helper.load_beatmaps_compact()["beatmaps"]
        bids = [bid for bid, beatmap in beatmaps.items() if beatmap["status"] in ["Ranked", "Loved"]]
        beatmap_links = Helper.load_beatmap_links()

        for bid in bids:
            subscores_dict = {}
            updated = int(beatmaps[str(bid)]["date"])
            msid = beatmap_links[str(bid)]
            sleep(REQUEST_INTERVAL)
            subscores = self.osu_api.beatmap_user_scores(bid, uid)
            if not subscores: continue
            for subscore in subscores:    
                score_dict = Helper.score_to_dict(subscore)
                sid = f"{uid}{score_dict["time"]}"
                score_dict["msid"] = msid
                score_dict["top"] = False
                if int(score_dict["time"]) < updated:
                    score_dict["old"] = True
                else:
                    score_dict["old"] = False

                subscores_dict |= {sid: score_dict}

            subscores_dict = dict(sorted(subscores_dict.items(), key=lambda score: int(score[1]["time"])))

            highest = 0
            for score in subscores_dict.values():
                if score["score"] > highest:
                    score["pb"] = True
                    highest = score["score"]

            subscores_dict = sorted(subscores_dict.items(), key=lambda score: score[1]["score"], reverse=True)
            subscores_dict[0][1]["top"] = True
            subscores_dict = dict(subscores_dict)

            user_dict["scores"] |= subscores_dict

            mapset_file = f"{msid}.json"
            if mapset_file in listdir(PATH_BEATMAPSETS):
                beatmapset = Helper.load_mapset(msid)
                beatmapset["beatmaps"][str(bid)]["scores"] |= subscores_dict
                with open(f"{PATH_BEATMAPSETS}/{mapset_file}", "w", encoding='utf-8') as f:
                    json.dump(beatmapset, f, ensure_ascii=False, indent=4)

        user_beatmapsets = {}

        for file in listdir(PATH_BEATMAPSETS):
            if not file.endswith(".json"): continue
            mapset = Helper.load_mapset(file[0:-5])
            msid = mapset["id"]
            _bids = []
            for _bid, beatmap in mapset["beatmaps"].items():
                if beatmap["mapper id"] == int(uid):
                    _bids.append(_bid)
            if _bids:
                user_beatmapsets |= {msid: _bids}

        user_dict["beatmapsets"] = user_beatmapsets

        with open(output, "w", encoding='utf-8') as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=4)

        states = ["R", "L", "U", "RL", "RLU"]
        keys = ["9", "10", "12", "14", "16", "18", "9+", "10+", "12+"]
        bid_keys = {}
        beatmaps_compact = Helper.load_beatmaps_compact()["beatmaps"]
        for bid, beatmap in beatmaps_compact.items():
            bid_keys |= {bid: (str(int(beatmap["keys"])), beatmap["status"])}

        self.process_pp_history_userfile(output, bid_keys, states, keys)
        subprocess.run([PATH_PYTHON, "scripts/daily_users_compact.py"], cwd=PATH_ROOT)

    def process_pp_history_userfile(self, file, bid_keys, states, keys):
        if not file.endswith(".json"): return
        with open(file, "r", encoding="utf-8") as f:
            user = json.load(f)

        pp_history = {}

        if user["scores"] == {}: return
        subscores = [score for score in user["scores"].values() if score["pb"] and not score["old"]]
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

                if k != "9" and k != "10":
                    key_groups.append("12+")

                status_groups = ["RLU"]
                if status == "Ranked":
                    status_groups += ["R", "RL"]

                elif status == "Loved":
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

        with open(file, "w", encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=4)
