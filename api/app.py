from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.routes.search import search_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(search_bp, url_prefix='/api/search')

def print_routes(app):
    print(">>> Registered routes:", file=sys.stderr)
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule}", file=sys.stderr)

print_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
