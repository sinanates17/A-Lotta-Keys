import sys
import os

project_root = os.path.dirname(os.path.dirname(__file__))  # one level above /api
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import logging
logging.basicConfig(stream=sys.stderr)

from api.app import app  # note: import from full path
application = app