from flask import Flask, render_template, session
from flask_cors import CORS
import sys
import secrets
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_ROOT, OSU_API_ID, OSU_API_SECRET, OSU_REDIRECT_URI
from api.routes.search import search_bp
from api.routes.auth import auth_bp

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
        return dict(logged_in=("user" in session), 
                    avatar_url=session.get("user").get("avatar url"),
                    id=session.get("user").get("id"))
    
    else:
        return dict(logged_in=("user" in session))

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
    app.run(debug=True)
