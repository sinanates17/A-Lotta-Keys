from flask import Flask, render_template
from flask_cors import CORS
import sys
import secrets
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_ROOT
from api.routes.search import search_bp

app = Flask(__name__, 
            template_folder=f"{PATH_ROOT}/frontend/html",
            static_folder=f"{PATH_ROOT}/frontend/static")
CORS(app)
app.register_blueprint(search_bp, url_prefix='/api/search')

app.secret_key = secrets.token_hex(32)

@app.route("/<file>")
def file(file):
    return render_template(file)

@app.route("/")
def home():
    return render_template("index.html")

def print_routes(app):
    print(">>> Registered routes:", file=sys.stderr)
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}", file=sys.stderr)

print_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
