from flask import Blueprint, jsonify, request, render_template, abort, current_app, redirect, url_for, session
import sys
import requests
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from datetime import datetime
from config import PATH_DATA, PATH_USERS, PATH_BEATMAPSETS, DISCORD_BOT_TOKEN, SERVER
from utils import Helper
from os import listdir
from api.routes.db import get_pf_db
from osu_db_tools.parse_scores import unpack_scores
import json
import traceback
import threading
import tempfile

DISCORD_API_BASE = "https://discord.com/api/v10"

auth_bp = Blueprint("auth", __name__)

def discord_dm(discord_uid: int, content):
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    r = requests.post(
        f"{DISCORD_API_BASE}/users/@me/channels",
        headers=headers,
        json={"recipient_id": discord_uid}
    )
    r.raise_for_status()
    dm_channel = r.json()["id"]

    r = requests.post(
        f"{DISCORD_API_BASE}/channels/{dm_channel}/messages",
        headers=headers,
        json={"content": content}
    )
    r.raise_for_status()

def build_profile(uid):
    helper = Helper()
    helper.initialize_user(uid)
    return

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

@auth_bp.route("/verify")
def verify():

    state = request.args.get("state")

    CLIENT_ID = current_app.config["CLIENT_ID"]
    CLIENT_SECRET = current_app.config["CLIENT_SECRET"]
    BOT_REDIRECT_URI = current_app.config["BOT_REDIRECT_URI"]

    return redirect(
        f"https://osu.ppy.sh/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={BOT_REDIRECT_URI}"
        f"&state={state}"
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

    def update_db():
        pf_db = get_pf_db()
        cur = pf_db.cursor()
        cur.execute("SELECT * FROM profiles WHERE uid = ?", (uid,))
        row = cur.fetchone()

        if not row:
            cur.execute("""
            INSERT INTO profiles (uid)
            VALUES (?)
            """, (uid,))
            pf_db.commit()

    if filename not in listdir(PATH_USERS):
        threading.Thread(target=build_profile, args=(uid,)).start()
        update_db()
        return redirect(url_for("auth.wait"))

    update_db()

    return redirect(url_for(f"search.user_page", uid=session["user"]["id"]))

@auth_bp.route("/callback_bot")
def callback_bot():
    try:
        CLIENT_ID = current_app.config["CLIENT_ID"]
        CLIENT_SECRET = current_app.config["CLIENT_SECRET"]
        BOT_REDIRECT_URI = current_app.config["BOT_REDIRECT_URI"]

        code = request.args.get("code")
        state = int(request.args.get("state"))

        if not code:
            return "No code received", 400

        token_response = requests.post("https://osu.ppy.sh/oauth/token", json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": BOT_REDIRECT_URI,
        })

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return "Failed to get access token", 400

        user_response = requests.get(
            "https://osu.ppy.sh/api/v2/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        uid = int(user_response.json()["id"])

        pf_db = get_pf_db()
        cur = pf_db.cursor()
        cur.execute("SELECT * FROM profiles WHERE uid = ?", (uid,))
        row = cur.fetchone()

        if not row:
            cur.execute("""
            INSERT INTO profiles (uid, discord_uid)
            VALUES (?, ?)
            """, (uid, state))

        cur.execute("""
            UPDATE profiles
            SET discord_uid = ?
            WHERE uid = ?
        """, (state, uid))

        pf_db.commit()

        warning = ""
        if f"{uid}.json" not in listdir(PATH_USERS):
            warning = f"\n\n**WARNING:** There is no profile for you on A Lotta Keys. Create one by logging in:\n{SERVER}/auth/login"

        discord_dm(int(state), f"Discord and osu! accounts are linked!{warning}")

        return redirect(url_for(f"auth.verified"))
    
    except Exception as e:
        print("Callback error:", e)
        traceback.print_exc()
        return "Internal server error", 500

@auth_bp.route("/verified")
def verified():
    return render_template("verified.html")

@auth_bp.route("/wait")
def wait():
    return render_template("wait.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@auth_bp.route("/setting_fav", methods=['POST'])
def setting_fav():
    data = request.get_json()
    setting_fav = data.get("settingFav")
    uid = data.get("id")

    pf_db = get_pf_db()
    cur = pf_db.cursor()
    cur.execute("""
        UPDATE profiles
        SET fav = ?
        WHERE uid = ?
    """, (setting_fav, uid))
    pf_db.commit()

    return jsonify({"status": "ok", "received": data})

@auth_bp.route("/upload_scores_db", methods=['POST'])
def upload_scores_db():
    def _process_db(db):
        db = dict(db[0])
        beatmap_hashes = Helper.load_beatmap_hashes()

        for hash, scores in db.items():
            try:
                bid = beatmap_hashes[hash]
                for score in scores:
                    score_dict = Helper.score_to_dict_db(score)
                    #Left off here
            except:
                continue

    if "db" not in request.files:
        return jsonify({"error": "No file"}), 400
    
    db_file = request.files["db"]
    if db_file.filename != "scores.db":
        return jsonify({"error": "Not scores.db"}), 400
    
    with tempfile.NamedTemporaryFile(delete=True, suffix=".db") as tmp:
        tmp.write(db_file.getvalue())
        tmp_path = tmp.name
        try:
            db = unpack_scores(tmp_path)
            threading.Thread(target=_process_db, args=(db,)).start()
            return jsonify({"status": "ok", "message": "Received. Check back in a few minutes."})
        except:
            return jsonify({"error": "scores.db seems corrupted"}), 400

    
