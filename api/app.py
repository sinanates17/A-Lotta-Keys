from flask import Flask
from flask import request
from flask_cors import CORS
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.routes.search import search_bp

app = Flask(__name__)

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.debug(f"[REQUEST] {request.method} {request.path}")

CORS(app)
app.register_blueprint(search_bp, url_prefix='/api/search')

if __name__ == '__main__':
    app.run(debug=True)