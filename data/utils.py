from ossapi import Ossapi, ossapi
from config import OSU_API_ID, OSU_API_SECRET, OSU_API_VERSION, DEBUG
from datetime import datetime
from time import sleep

class Helper:
    def __init__(self, prefix="[DATA_UTILS] "):
        self.prefix = prefix
        self.osu_api = Ossapi(client_id=OSU_API_ID, client_secret=OSU_API_SECRET, api_version=OSU_API_VERSION)

    def beatmapset_to_dict(self, beatmapset: ossapi.Beatmapset):

        beatmapset_dict = {
            'artist' : beatmapset.artist,
            'artist_unicode' : beatmapset.artist_unicode,
            'beatmaps' : [self.beatmap_to_dict(diff) for diff in beatmapset.beatmaps],
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
    
    def beatmap_to_dict(self, beatmap: ossapi.Beatmap):

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
            'fail times': beatmap.failtimes.fail,
            'exit times': beatmap.failtimes.exit,
            'hit length': beatmap.hit_length,
            'id': beatmap.id,
            'last updated': [beatmap.last_updated.month, beatmap.last_updated.day, beatmap.last_updated.year, beatmap.last_updated.hour]
                if isinstance(beatmap.last_updated, datetime) else None,
            'max combo': beatmap.max_combo,
            'mode': beatmap.mode.value,
            'mode int': beatmap.mode_int,
            'owner': beatmap.owner, #TEST THIS
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
    
    def score_to_dict(self, score: ossapi.Score):

        score_dict = {
            'accuracy': score.accuracy,
            'beatmap id': score.beatmap_id,
            'best id': score.best_id,
            'build id': score.build_id,
            'classic total score': score.classic_total_score,
            'ended at': [score.ended_at.month, score.ended_at.day, score.ended_at.year, score.ended_at.hour]
                if isinstance(score.ended_at, datetime) else None,
            'has replay': score.has_replay,
            'id': score.id,
            'is perfect combo': score.is_perfect_combo,
            'legacy perfect': score.legacy_perfect,
            'legacy score id': score.legacy_score_id,
            'legacy total score': score.legacy_total_score,
            'max combo': score.max_combo,
            'mods': bin(score.mods.value),
            'passed': score.passed,
            'pp': score.pp,
            'rank': score.rank.value,
            'rank country': score.rank_country,
            'rank global': score.rank_global,
            'ranked': score.ranked,
            'replay': score.replay,
            'ruleset id': score.ruleset_id,
            'started at': [score.started_at.month, score.started_at.day, score.started_at.year, score.started_at.hour] 
                if isinstance(score.started_at, datetime) else None,
            'statistics': self.score_statistics_to_dict(score.statistics),
            'total score': score.total_score,
            'total score without mods': score.total_score_without_mods,
            'type': score.type,
            'user id': score.user_id,
            'weight': score.weight
        }

        return score_dict

    def score_statistics_to_dict(self, stats: ossapi.Statistics):

        statistics_dict = {
            'combo break': stats.combo_break,
            'good': stats.good,
            'great': stats.great,
            'ignore hit': stats.ignore_hit,
            'ignore miss': stats.ignore_miss,
            'large bonus': stats.large_bonus,
            'large tick hit': stats.large_tick_hit,
            'large tick miss': stats.large_tick_miss,
            'legacy combo increase': stats.legacy_combo_increase,
            'meh': stats.meh,
            'miss': stats.miss,
            'ok': stats.ok,
            'perfect': stats.perfect,
            'slider tail hit': stats.slider_tail_hit,
            'small bonus': stats.small_bonus,
            'small tick hit': stats.small_tick_hit,
            'small tick miss': stats.small_tick_miss
        }
        
        return statistics_dict
    
    def cum_search_beatmapsets(self,**kwargs) -> list[Ossapi.beatmapset]:
        result = self.osu_api.search_beatmapsets(**kwargs)
        total = result.beatmapsets
        page = 1
        print(f'Page {page}') #Temporary until I implement a logger

        while result.cursor is not None:
            sleep(3)
            page += 1
            print(f'Page {page}') #Temporary until I implement a logger
            result = self.osu_api.search_beatmapsets(**kwargs, cursor=result.cursor)

            for beatmapset in result.beatmapsets:
                print(beatmapset.title) #Temporary until I implement a logger
                total.append(beatmapset)

        return total