from flask import Flask, render_template, session, g, send_from_directory, Response, url_for
from flask_cors import CORS
from os import listdir
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import secrets
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_ROOT, OSU_API_ID, OSU_API_SECRET, OSU_REDIRECT_URI, PATH_DATA, BOT_REDIRECT_URI
from api.routes.search import search_bp
from api.routes.auth import auth_bp
from api.routes.db import get_pf_db, DATABASE
from utils import Helper
import sqlite3
from pathlib import Path
import json
import redis

app = Flask(__name__, 
            template_folder=f"{PATH_ROOT}/frontend/html",
            static_folder=f"{PATH_ROOT}/frontend/static")
CORS(app)

r = redis.Redis(host='localhost', port=6379, db=0)

THEMES_DIR = f"{PATH_ROOT}/frontend/static/themes"
THEMES = listdir(THEMES_DIR)
current_theme = THEMES[0]

app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
app.config["CLIENT_ID"] = OSU_API_ID
app.config["CLIENT_SECRET"] = OSU_API_SECRET
app.config["REDIRECT_URI"] = OSU_REDIRECT_URI
app.config["BOT_REDIRECT_URI"] = BOT_REDIRECT_URI
app.secret_key = secrets.token_hex(32)

app.register_blueprint(search_bp, url_prefix='/api/search')
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.context_processor
def logged_in():
    if "user" in session:
        uid = session.get("user").get("id")

        pf_db = get_pf_db()
        cur = pf_db.cursor()
        cur.execute("SELECT * FROM profiles WHERE uid = ?", (uid,))
        row = dict(cur.fetchone())

        session_settings = {
            key: value for key, value in row.items()
        }

        return dict(logged_in=("user" in session), 
                    avatar_url=session.get("user").get("avatar url"),
                    id=uid,
                    session_settings=session_settings)
    
    else:
        return dict(logged_in=("user" in session))

@app.route("/favicon.ico")
def serve_favicon():
    path = f"{THEMES_DIR}/{current_theme}"
    return send_from_directory(path, "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/styles")
def styles():
    theme_dir = f"{THEMES_DIR}/{current_theme}"
    theme_json = f"{theme_dir}/theme.json"

    with open(theme_json, "r", encoding="utf-8") as f:
        theme = json.load(f)

    css = render_template('styles.css.j2', theme=theme)
    return Response(css, mimetype="text/css")

@app.teardown_request
def close_pf_db(exception):
    pf_db = g.pop("pf_db", None)
    if pf_db is not None:
        pf_db.close()

def init_pf_db():
    pf_db = sqlite3.connect(DATABASE)
    pf_db.execute("PRAGMA journal_mode=WAL;")
    pf_db.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            uid INTEGER PRIMARY KEY,
            discord_uid INTEGER
            fav TEXT
        );
    """)
    cur = pf_db.cursor()
    cur.execute(f"PRAGMA table_info(profiles)")
    columns = [info[1] for info in cur.fetchall()]
    if "discord_uid" not in columns:
        pf_db.execute(f"ALTER TABLE profiles ADD COLUMN discord_uid INTEGER")

    pf_db.commit()
    pf_db.close()

@app.route("/<file>")
def file(file):
    return render_template(file)

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        app.static_folder,
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon')

def print_routes(app):
    print(">>> Registered routes:", file=sys.stderr)
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}", file=sys.stderr)

def rotate_theme():
    global current_theme
    num_themes = len(THEMES)
    i = THEMES.index(current_theme)
    i = (i + 1) % num_themes
    current_theme = THEMES[i]

    r.publish("theme_rotate", current_theme)

scheduler = BackgroundScheduler()
scheduler.add_job(rotate_theme, trigger="interval", seconds=5)

if __name__ == '__main__':
    init_pf_db()
    scheduler.start()
    app.run(debug=True)
    print_routes(app)
