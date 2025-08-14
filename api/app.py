from flask import Flask, render_template, session, g
from flask_cors import CORS
import sys
import secrets
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_ROOT, OSU_API_ID, OSU_API_SECRET, OSU_REDIRECT_URI, PATH_DATA
from api.routes.search import search_bp
from api.routes.auth import auth_bp
from api.routes.db import get_pf_db
from utils import Helper
import sqlite3
from pathlib import Path

app = Flask(__name__, 
            template_folder=f"{PATH_ROOT}/frontend/html",
            static_folder=f"{PATH_ROOT}/frontend/static")
CORS(app)

app.config["CLIENT_ID"] = OSU_API_ID
app.config["CLIENT_SECRET"] = OSU_API_SECRET
app.config["REDIRECT_URI"] = OSU_REDIRECT_URI
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

@app.teardown_request
def close_pf_db(exception):
    pf_db = g.pop("pf_db", None)
    if pf_db is not None:
        pf_db.close()

@app.route("/<file>")
def file(file):
    return render_template(file)

@app.route("/")
def home():
    return render_template("home.html")

def print_routes(app):
    print(">>> Registered routes:", file=sys.stderr)
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}", file=sys.stderr)

print_routes(app)

if __name__ == '__main__':
    pf_path = Path(f"{PATH_DATA}/profiles.sqlite")
    pf_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(pf_path)

    conn.execute("PRAGMA journal_mode=WAL;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        uid             INTEGER PRIMARY KEY,
        fav             TEXT
    );
    """)

    conn.commit()

    app.run(debug=True)
