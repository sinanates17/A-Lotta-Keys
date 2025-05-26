from flask import Blueprint, jsonify, request
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import PATH_DATA
import json

search_bp = Blueprint("search", __name__)

def load_user_compact():
    with open(f"{PATH_DATA}/users_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)
    return compact

def load_beatmap_compact():
    with open(f"{PATH_DATA}/beatmaps_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)
    return compact 

@search_bp.route("/users", methods=["GET"])
def get_users():
    print("Searching users")
    filters = request.args.getlist("key")
    sort = request.args.get("sort")
    users = load_user_compact()
    users = users["users"]
    beatmaps = load_beatmap_compact()
    num_unranked = sum([beatmaps["unranked"][k] for k in filters])
    num_ranked = sum([beatmaps["ranked"][k] for k in filters] +
                     [beatmaps["loved"][k] for k in filters])
    del beatmaps #Look at me I'm manually managing memory in python!

    response = []
    for user in users.values():
        rscore = sum([user["ranked score"][k] for k in filters])
        tscore = sum([user["ranked score"][k] for k in filters])
        rperc = round(100 * rscore/(num_ranked*1000000), 2)
        tperc = round(100 * tscore/((num_ranked+num_unranked)*1000000), 2)

        row = {
            "name": user["name"],
            "rscore": rscore,
            "rperc": rperc,
            "tscore": tscore,
            "tperc": tperc,
            "numscores": sum([user["num scores"][k] for k in filters]),
            "beatmap plays": sum([user["beatmap plays"][k] for k in filters]),
            "last score": user["last score"] if user["last score"] < 60 else ">60",
            "country": user["country"]}
        
        response.append(row)
        response.sort(key=lambda x: x[sort], reverse=True)
        i = 1
        for row in response:
            row["pos"] = i
            i += 1

    return jsonify(response)

@search_bp.route("/beatmaps", methods=["GET"])
def get_beatmaps():
    filters = request.args.getlist("option")
    beatmaps = load_beatmap_compact()
