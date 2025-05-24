from ossapi import Ossapi, Beatmapset, Beatmap, Score, User, Statistics
from config import OSU_API_ID, OSU_API_SECRET, REQUEST_INTERVAL, PATH_USERS
from datetime import datetime, timezone
from time import sleep
from os import listdir
import json

class Helper:
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
            'bid': int(score.beatmap_id) if isinstance(score.beatmap_id, str) else int(score.beatmap.id),
            'msid': score.beatmapset.id,
            'time': score.ended_at.strftime("%y%m%d%H%M%S"),
            'mods': [mod.acronym for mod in score.mods],
            'combo': score.max_combo,
            'passed': score.passed,
            'pp': score.pp,
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
            results = self.osu_api.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user_id)
            for result in results: #This is a monkey patch since beatmap_user_scores() doesnt include a beatmap or beatmap id in the returned scores.
                result.beatmap_id = beatmap_id
            scores += results

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

        sleep(REQUEST_INTERVAL)
        users = []
        for sublist in sublists:
            users += self.osu_api.users(user_ids=sublist)
        return users
    
    def user_scores_recent(self, user_id: int) -> list[Score]:
        sleep(REQUEST_INTERVAL)
        scores = self.osu_api.user_scores(user_id=user_id, type="recent", limit=200)
        return scores