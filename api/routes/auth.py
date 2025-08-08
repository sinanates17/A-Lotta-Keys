from flask import Blueprint, jsonify, request, render_template, abort, current_app, redirect, url_for, session
import sys
import requests
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from datetime import datetime
from config import PATH_DATA, PATH_USERS, PATH_BEATMAPSETS
from utils import Helper
from os import listdir
import json

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login")
def login():

    CLIENT_ID = current_app.config["CLIENT_ID"]
    CLIENT_SECRET = current_app.config["CLIENT_SECRET"]
    REDIRECT_URI = current_app.config["REDIRECT_URI"]

    return redirect(
        f"https://osu.ppy.sh/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
    )

@auth_bp.route("/callback")
def callback():

    CLIENT_ID = current_app.config["CLIENT_ID"]
    CLIENT_SECRET = current_app.config["CLIENT_SECRET"]
    REDIRECT_URI = current_app.config["REDIRECT_URI"]

    code = request.args.get("code")
    if not code:
        return "No code received", 400

    token_response = requests.post("https://osu.ppy.sh/oauth/token", json={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    })

    token_data = token_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        return "Failed to get access token", 400

    user_response = requests.get(
        "https://osu.ppy.sh/api/v2/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    uid = user_response.json()["id"]
    session["user"] = {}
    session["user"]["id"] = uid
    session["user"]["avatar url"] = user_response.json()["avatar_url"]

    filename = f"{uid}.json"
    output = f"{PATH_USERS}/{filename}"

    if filename not in listdir(PATH_USERS):
        helper = Helper()
        user = helper.osu_api.user(uid)
        user_dict = Helper.user_to_dict(user)
        user_dict["settings"] = {}

        with open (output, "w", encoding='utf-8') as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=4)

    else:
         user = Helper.load_user(uid)

         if "settings" not in user.keys():
            user["settings"] = {}

            with open(output, "w", encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=4)

    return redirect(url_for(f"search.user_page", uid=session["user"]["id"]))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@auth_bp.route("/setting_fav", methods=['POST'])
def setting_fav():
    data = request.get_json()
    settingFav = data.get("settingFav")
    uid = data.get("id")

    user = Helper.load_user(uid)

    user["settings"]["fav"] = settingFav

    output = f"{PATH_USERS}/{uid}.json"

    with open (output, "w", encoding='utf-8') as f:
        json.dump(user, f, ensure_ascii=False, indent=4)

    return jsonify({"status": "ok", "received": data})
