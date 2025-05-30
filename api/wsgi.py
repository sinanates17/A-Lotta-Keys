import sys
import os

api_path = os.path.dirname(__file__)
sys.path.insert(0, api_path)

import logging
logging.basicConfig(stream=sys.stderr)

from app import app

application = app 