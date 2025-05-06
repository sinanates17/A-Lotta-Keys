from ossapi import Ossapi, ossapi, Beatmapset, Beatmap, Score, Statistics
from config import OSU_API_ID, OSU_API_SECRET, DEBUG
from datetime import datetime
from time import sleep

OSU_API_VERSION = 20220704

class Helper:
    def __init__(self, prefix="[Helper] "):
        self.prefix = prefix
        self.osu_api = Ossapi(client_id=OSU_API_ID, client_secret=OSU_API_SECRET, api_version=OSU_API_VERSION)

    @staticmethod
    def beatmapset_to_dict(beatmapset: Beatmapset):
        beatmapset_dict = {
            'artist' : beatmapset.artist,
            'artist_unicode' : beatmapset.artist_unicode,
            'beatmaps' : [Helper.beatmap_to_dict(diff) for diff in beatmapset.beatmaps],
            'bpm': beatmapset.bpm,
            'creator': beatmapset.creator,
            'description': beatmapset.description,
            'favourite count': beatmapset.favourite_count,
            'id': beatmapset.id,
            'is scorable': beatmapset.is_scoreable,
            'last updated': [beatmapset.last_updated.month, beatmapset.last_updated.day, beatmapset.last_updated.year, beatmapset.last_updated.hour]
                if isinstance(beatmapset.last_updated, datetime) else None,
            'play count': beatmapset.play_count,
            'ranked': beatmapset.ranked.value, #A:2 G:-2 L:4 P:0 Q:3 R:1 W:-1
            'ranked_date': [beatmapset.ranked_date.month, beatmapset.ranked_date.day, beatmapset.ranked_date.year, beatmapset.ranked_date.hour]
                if isinstance(beatmapset.ranked_date, datetime) else None,
            'source':  beatmapset.source,
            'spotlight':  beatmapset.spotlight,
            'status': beatmapset.status.value,
            'submitted date': [beatmapset.submitted_date.month, beatmapset.submitted_date.day, beatmapset.submitted_date.year, beatmapset.submitted_date.hour]
                if isinstance(beatmapset.submitted_date, datetime) else None,
            'tags': beatmapset.tags,
            'title': beatmapset.title,
            'title unicode': beatmapset.title_unicode,
            'track id': beatmapset.track_id,
            'user id': beatmapset.user_id
        }

        return beatmapset_dict
    
    @staticmethod
    def beatmap_to_dict(beatmap: Beatmap):

        beatmap_dict = {
            'accuracy': beatmap.accuracy,
            'ar': beatmap.ar,
            'beatmapset id': beatmap.beatmapset_id,
            'bpm': beatmap.bpm,
            'checksum': beatmap.checksum,
            'count circles': beatmap.count_circles,
            'count sliders': beatmap.count_sliders,
            'count spinners': beatmap.count_spinners,
            'cs': beatmap.cs,
            'difficulty rating': beatmap.difficulty_rating,
            'drain': beatmap.drain,
            #'fail times': beatmap.failtimes.fail,
            #'exit times': beatmap.failtimes.exit,
            'hit length': beatmap.hit_length,
            'id': beatmap.id,
            'last updated': [beatmap.last_updated.month, beatmap.last_updated.day, beatmap.last_updated.year, beatmap.last_updated.hour]
                if isinstance(beatmap.last_updated, datetime) else None,
            'max combo': beatmap.max_combo,
            'mode': beatmap.mode.value,
            'mode int': beatmap.mode_int,
            'owner': beatmap.owner,
            'passcount': beatmap.passcount,
            'playcount': beatmap.playcount,
            'ranked': beatmap.ranked.value,
            'status': beatmap.status.value,
            'total length': beatmap.total_length,
            'url': beatmap.url,
            'user id': beatmap.user_id,
            'version': beatmap.version
        }

        return beatmap_dict
    
    @staticmethod
    def score_to_dict(score: Score): #Intended for API version 20220704

        score_dict = {
            'acc': score.accuracy,
            'map id': score.beatmap_id if isinstance(score.beatmap_id, int) else score.beatmap.id,
            'time': [score.created_at.month, score.created_at.day, score.created_at.year, score.created_at.hour, score.created_at.minute]
                if isinstance(score.created_at, datetime) else None,
            'replay': score.replay,
            'id': score.id,
            'pf': score.perfect,
            'max combo': score.max_combo,
            'mods': bin(score.mods.value),
            'passed': score.passed,
            'pp': score.pp,
            'rank': score.rank.value,
            'ranked': score.ranked,
            'stats': Helper.score_statistics_to_dict(score.statistics),
            'score': score.score,
            'user id': score.user_id,
            'int id': f"{score.user_id}{score.created_at.strftime("%d%m%Y%H%M%S")}"
        }

        return score_dict

    @staticmethod
    def score_statistics_to_dict(stats: Statistics):

        statistics_dict = { #Intended for API version 20220704
            '50': stats.count_50,
            '100': stats.count_100,
            '300': stats.count_300,
            'geki': stats.count_geki,
            'katu': stats.count_katu,
            '0': stats.count_miss,
        }
        
        return statistics_dict
    
    def cum_search_beatmapsets(self,**kwargs) -> list[Ossapi.beatmapset]:
        result = self.osu_api.search_beatmapsets(**kwargs)
        total = result.beatmapsets
        page = 1
        print(f'Page {page}') #Temporary until I implement a logger

        while result.cursor is not None:
            sleep(2)
            page += 1
            print(f'Page {page}') #Temporary until I implement a logger
            result = self.osu_api.search_beatmapsets(**kwargs, cursor=result.cursor)

            for beatmapset in result.beatmapsets:
                #print(beatmapset.title) #Temporary until I implement a logger
                total.append(beatmapset)

        return total
    
    def user_scores_many_beatmaps(self, user_id: int, beatmap_ids: list[int]) -> list[Score]:
        scores = []
        length = len(beatmap_ids)

        for i, beatmap_id in enumerate(beatmap_ids):
            sleep(2)
            print(f"Request {i} of {length}") #Temporary until I implement a logger
            results = self.osu_api.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user_id)
            for result in results: #This is a monkey patch since beatmap_user_scores() doesnt include a beatmap or beatmap id in the returned scores.
                result.beatmap_id = beatmap_id
            scores += results

        return scores
    
    def user_ids_per_beatmap(self, beatmap_ids: list[int]) -> dict[int:list[int]]:
        beatmap_ids_w_user_ids = { id:[] for id in beatmap_ids}

        for i, beatmap_id in enumerate(beatmap_ids):
            sleep(2)
            beatmap_scores = self.osu_api.beatmap_scores(beatmap_id=beatmap_id, limit=100).scores
            beatmap_ids_w_user_ids[beatmap_id] = [score.user_id for score in beatmap_scores]
            print(f"Beatmap {i+1} of {len(beatmap_ids)} | {len(beatmap_scores)} users")

        return beatmap_ids_w_user_ids
    
    def beatmap_user_scores(self, beatmap_id: int, user_id: int, **kwargs) -> list[Score]:
        sleep(2)
        scores = self.osu_api.beatmap_user_scores(beatmap_id=beatmap_id, user_id=user_id, **kwargs)

        for score in scores: #This is a monkey patch since beatmap_user_scores() doesnt include a beatmap or beatmap id in the returned scores.
            score.beatmap_id = beatmap_id
        
        return scores