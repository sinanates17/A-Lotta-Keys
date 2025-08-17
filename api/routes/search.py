from flask import Blueprint, jsonify, request, render_template, abort, g, redirect, url_for
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from datetime import datetime
from config import PATH_DATA, PATH_USERS, PATH_BEATMAPSETS
from utils import Helper
import json
from pathlib import Path
import sqlite3
from api.routes.db import get_pf_db
from os import listdir

search_bp = Blueprint("search", __name__)

def load_user_compact():
    with open(f"{PATH_DATA}/users_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)

    return compact

def load_beatmap_compact():
    with open(f"{PATH_DATA}/beatmaps_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)

    return compact 

def load_user_links():
    with open(f"{PATH_DATA}/user_links.json", "r", encoding="utf-8") as f:
        links = json.load(f)

    return links

def msid_from_bid(bid):
    with open(f"{PATH_DATA}/beatmap_links.json", "r", encoding="utf-8") as f:
        links = json.load(f)

    msid = links[str(bid)]
    return msid

@search_bp.route("/users", methods=["GET"])
def get_users():
    filters = request.args.getlist("key")
    sort = request.args.get("sort")
    reverse = request.args.get("reverse") == "True"
    country = request.args.get("country")
    pp_state = request.args.get("pp")
    pp_keys = None
    users = load_user_compact()
    users = users["users"]
    beatmaps = load_beatmap_compact()
    num_unranked = sum([beatmaps["unranked"][k] for k in filters])
    num_ranked = sum([beatmaps["ranked"][k] for k in filters] +
                     [beatmaps["loved"][k] for k in filters])
    
    del beatmaps #Look at me I'm manually managing memory in python!

    if len(filters) == 1:
        pp_keys = filters[0]

    if set(filters) == {"9", "10", "12", "14", "16", "18"}:
        pp_keys = "9+"

    if set(filters) == {"10", "12", "14", "16", "18"}:
        pp_keys = "10+"

    if set(filters) == {"12", "14", "16", "18"}:
        pp_keys = "12+"

    response = []
    for id, user in users.items():
        if not country.lower() in user["country"].lower() and country != '':
            continue

        rscore = sum([user["ranked score"][k] for k in filters])
        tscore = sum([user["total score"][k] for k in filters])
        rperc = round(100 * rscore/(num_ranked*1000000), 2)
        tperc = round(100 * tscore/((num_ranked+num_unranked)*1000000), 2)

        rscore = f"{str(round(rscore/1000000, 1))} M"
        tscore = f"{str(round(tscore/1000000, 1))} M"

        row = {
            "id": id,
            "name": user["name"],
            "pp": user["pps"][pp_state][pp_keys] if pp_keys is not None else "-",
            "rscore": rscore,
            "rperc": rperc,
            "tscore": tscore,
            "tperc": tperc,
            "numscores": sum([user["num scores"][k] for k in filters]),
            "beatmap plays": sum([user["beatmap plays"][k] for k in filters]),
            "last score": user["last score"] if user["last score"] < 60 else ">60",
            "country": user["country"]}
        
        response.append(row)

    response.sort(key=lambda x: x[sort], reverse=not reverse)
    i = 1
    for row in response:
        row["pos"] = i
        i += 1

    return jsonify(response)

@search_bp.route("/beatmaps", methods=["GET"])
def get_beatmaps():
    filters = request.args.getlist("key")
    sort = request.args.get("sort")
    reverse = request.args.get("reverse") == "True"
    states = request.args.getlist("status")
    beatmaps = load_beatmap_compact()
    beatmaps = beatmaps["beatmaps"]

    response = []
    for bid, beatmap in beatmaps.items():
        if str(int(beatmap["keys"])) not in filters: continue
        if beatmap["status"] not in states: continue
        lnperc = round(beatmap["ln perc"], 2)
        recent = int(beatmap["date"])
        row = {
            "id": bid,
            "name":beatmap["name"],
            "mapper":beatmap["mapper"],
            "keys":beatmap["keys"],
            "sr":beatmap["sr"],
            "plays":beatmap["plays"],
            "passes":beatmap["passes"],
            "length":beatmap["length"],
            "ln perc":lnperc,
            "status":beatmap["status"],
            "recent":recent}

        response.append(row)

    response.sort(key=lambda x: x[sort], reverse=not reverse)
    print(reverse)
    i = 1
    for row in response:
        row["pos"] = i
        i += 1

    return jsonify(response)

@search_bp.route("/users/<uid>", methods=["GET"])
def user_page(uid):
    if f"{uid}.json" not in listdir(PATH_USERS):
        return redirect(url_for("auth.wait"))

    users = load_user_compact()
    beatmaps_compact = load_beatmap_compact()
    beatmaps = { bid: {"name": beatmap["name"], 
                       "status": beatmap["status"],
                       "keys": beatmap["keys"]} 
                       for bid, beatmap in beatmaps_compact["beatmaps"].items() }
    users = users["users"]
    user_compact = users.get(uid)

    user = Helper.load_user(uid)

    self_bmids = []

    for bmids in user["beatmapsets"].values():
        self_bmids += bmids

    self_beatmaps = { bid: beatmaps_compact["beatmaps"].get(bid, {}) for bid in self_bmids }
    self_beatmaps = { bid: {**bm, "bid": bid} for bid, bm in self_beatmaps.items() if bm != {} }

    pf_db = get_pf_db()
    cur = pf_db.cursor()
    cur.execute("SELECT * FROM profiles WHERE uid = ?", (uid,))
    row = cur.fetchone()

    if row:
        row = dict(row)
        settings = {
            "fav": row.get("fav", "")
        }
    else:
        settings = {}

    return render_template("user.html", user=user, compact=user_compact, beatmaps=beatmaps, self_beatmaps=self_beatmaps, user_settings=settings)

@search_bp.route("/beatmaps/<bid>", methods=["GET"])
def beatmap_page(bid):

    user_links = load_user_links()

    def rowify(score):
        return {"uid": score["uid"],
                "player": user_links[str(score["uid"])],
                "pp": round(score["pp"], 2),
                "score": score["score"],
                "acc": round(score["acc"] * 100, 2),
                "combo": score["combo"],
                "ratio": round(score["320"] / score["300"], 2) if score["300"] > 0 else "-",
                "marv": score["320"],
                "perf": score["300"],
                "great": score["200"],
                "good": score["100"],
                "bad": score["50"],
                "miss": score["0"],
                "date": datetime.strptime(score["time"], "%y%m%d%H%M%S").strftime("%-d %b %Y"),
                "old": score["old"]}

    msid = msid_from_bid(bid)

    beatmapset = Helper.load_mapset(msid)

    beatmap = beatmapset["beatmaps"][bid]
    title = beatmapset["title"]
    artist = beatmapset["artist"]
    ranked = beatmapset["ranked"]
    mapper = user_links.get(str(beatmap["mapper id"]), "null")

    scores = beatmapset["beatmaps"][bid]["scores"]

    pbs = {}

    for score in scores.values():
        uid = str(score["uid"])

        if uid not in pbs.keys():
            pbs[uid] = rowify(score)
            continue

        if score["score"] > pbs[uid]["score"]:
            pbs[uid] = rowify(score)

    pbs = list(pbs.values())

    pbs.sort(key=lambda x: x["score"], reverse=True)

    i = 1
    for pb in pbs:
        pb["pos"] = i
        i += 1

    return render_template("beatmap.html", beatmap=beatmap, title=title, artist=artist, mapper=mapper, userLinks=user_links, pbs=pbs, ranked=ranked)

@search_bp.route("/discord/<discord_uid>", methods=["GET"])
def profile_from_discord_uid(discord_uid):
    pf_db = get_pf_db()
    cur = pf_db.cursor()
    cur.execute("SELECT * FROM profiles WHERE discord_uid = ?", (discord_uid,))
    row = cur.fetchone()
    row = dict(row)
    if row:
        return jsonify(row)
    else:
        return jsonify({"error": "not found"}), 404
    