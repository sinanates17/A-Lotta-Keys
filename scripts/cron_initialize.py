"""
This script and its children are meant to be run only once, at the release of this project. 

Parent script: cron_initialize.py

Child script 1: initialize_beatmaps.py
    - Request every 9K+ beatmapset.
    - For every beatmapset:
        - Filter out non-9K+ difficulties.
        - Generate a JSON for the mapset with the format below and fill out everything but 'beatmaps'
        - For each difficulty, create a beatmapid entry for the 'beatmaps' dict and fill out the following
                diffname        title           artist
                host            mapper          status
                submitted at    last updated    ranked at
                total plays     total passes
            - Scores should be initialized to an empty dictionary.
            - Players to an empty list.
            - Plays and passes over time to a dictionary with one timestamp:int entry.
    
Child script 2: initialize_scores.py
    - Loop through every beatmapsetid.json and generate a list of all beatmap ids that have a leaderboard.
    - For each leaderboard beatmap:
        - Request the top 100 scores.
        - Get a list of user ids included in those scores.
        - Set the beatmap's 'players' value to that list.
        - For every user in every leaderboarded beatmap:
            - Request the user's scores on the beatmap and accumulate the scores in a raw list.
        - Process the raw list of scores into a dictionary and dump it to a JSON with the format below.

Child script 3: initialize_users.py
    - Loop through every scores.json dump (there should only be one) and get the list of unique user ids.
    - Request each user, generate a Userid.json for each with the format below, and fill out name and avatar url.
        - Initialize tracking to True and days since last score to 0.
        - Initialize scores to an empty dictionary.
        - Initialize beatmapsets to an empty dictionary
        - Initialize total beatmap and lb beatmap plays to empty dictionaries

Child script 4: initialize_network.py
    - Import the scores.json dumps (there should only be one at this point), but generalize the code anyway
    - For each score:
        - Append scoreid:score to the beatmap's 'scores' dictionary
        - Merge the player's user id into the beatmap's 'players' list
    - Import the scores.json dumps (there should only be one at this point), but generalize the code anyway.
    - For each user.json:
        - For each score in the score.json dumps:
            - Append scoreid:score to the user's 'scores' dictionary if the score matches the user
        - Parse through the scores and keep track of the most recent one.
            - If most recent is >60 days ago, set tracking to False
        - For each beatmap.json, append the beatmap id to the user's 'beatmap ids if the user made the beatmap.
            - Keep track of the total plays and passes for each user
        - Create an initial timestamp:total entry for plays and passes over time


Beatmapsetid.json layout, one JSON per beatmapset to avoid large files, each continuously updated:

{       
        'id' : int                          |
        'title': str                        |
        'artist': str                       |
        'titleu': str                       |
        'artistu: str                       |
        'favs' : int                        |
        'desc' : str                        |
        'source' : str                      |
        'tags' : str                        |
        'host id' : str                     |
        'submitted' : str                   |
        'ranked' : str                      | MMDDYYhhmmss
        'beatmaps' : dict {                 |
            id1: dict {                     | id1 is an int
                'diffname' : str            |
                'sr' : float                |
                'bpm' : float               |
                'mapper id' : int           |
                'status' : int              | G-2 | W-1 | P 0 | R 1 | A 2 | Q 3 | L 4
                'updated' : str             | MMDDYYhhmmss UTC
                'ranked' : str              | MMDDYYhhmmss UTC, 'unranked' if no leaderboard
                'url' : str                 |
                'drain' : float             |
                'rice' : int                |
                'ln' : int                  |
                'players' : list[int]       | Keep track of which userids have scores on this map
                'scores : dict {...}        | Each key is an internally generated id, the value is a dict with the scoreid1 format below
                'total plays' : int         |
                'total passes' : int        |
                'plays over time' : dict {  |
                    timestamp : int         | Ordered pairs representing a graph of playcount, timestamp is a string formatted MMDDYY.
                    timestamp : int         |
                    ⋮⋮                       |
                    ⋮⋮                       |
                }                           |
                'passes over time' : dict { |
                    timestamp : int         | Ordered pairs representing a graph of playcount, timestamp is a string formatted MMDDYY.
                    timestamp : int         |
                    ⋮⋮                       |
                    ⋮⋮                       |
            }                               |
            id2: dict {...}                 |
            ⋮⋮                               |
            ⋮⋮                               |
        }                                   |
    }                                       |
}                                           |

Userid.json layout, one JSON per user to avoid large files, each continuously updated:

{                                           |
        'id' : int                          |
        'name' : str                        |
        'avatar url' : str                  |
        'days ago' : int                    | Not for display, this just turns tracking off if it gets >60, at which point it will stop updating.
        'tracking' : bool                   |
        'scores' : dict {...}               | Each key is an internally generated id, the value is a dict with the scoreid1 format below
        'beatmapsets' : dict {              | Reference dictionary to look up beatmaps in their respective JSON, doesnt contain all data.
            id1 : list[int]                 | List of beatmap ids. This dict includes the user's GDs and excludes GDs made for the user.
            id2 : list[int]                 |
            ⋮⋮                               |
            ⋮⋮                               |
        }                                   |
        'total beatmap plays' : dict {      | Includes 9K
            timestamp : int                 | Ordered pairs representing a graph of playcount, timestamp is a string formatted MMDDYY.
            timestamp : int                 |
            ⋮⋮                               |
            ⋮⋮                               |
        }                                   | Every score has 3 copies of itself stored, one in the dump, one under a user, and one under a beatmap.
                                            | While this is not very storage efficient, it's very convenient, and storage isn't a concern with how
}                                           | relatively small the corpus of 9K+ is

ScoresMMDDYYhhmmss.json layout, each JSON containing a dump of scores:

{                                           |
    'timestamp': str                        | MMDDYYhhmmss UTC, this is metadata for the .json
    scoreid1 : dict {                       | scoreid1, 2 etc. are not actual score ids, they're internally generated from the userid and timestamp.
        'uid' : int                         | User id
        'bid : int                          | Beatmap id
        'time' : str                        | MMDDYYhhmmss
        'mods' : list[str]                  |
        'combo' : int                       |
        'passed' : bool                     |
        'pp' : float                        |
        'acc' : float                       |
        'grade' : str                       |
        'score' : int                       |
        '320' : int                         |
        '300' : int                         |
        '200' : int                         |
        '100' : int                         |
        '50' : int                          |
        '0' : int                           |
    }                                       |
    scoreid2 : dict{...}                    |
    ⋮⋮                                       |
    ⋮⋮                                       |
}                                           |

"""

import subprocess
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PYTHON_PATH

def main():
    subprocess.run([PYTHON_PATH, "scripts/initialize_beatmaps.py"])
    subprocess.run([PYTHON_PATH, "scripts/initialize_scores.py"])
    subprocess.run([PYTHON_PATH, "scripts/initialize_users.py"])
    subprocess.run([PYTHON_PATH, "scripts/initialize_network.py"])

if __name__ == "__main__":
    main()