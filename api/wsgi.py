import sys
import os
import logging

# Set up logging early
logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.debug("WSGI startup...")

# Add project root (one level above 'api')
project_root = os.path.dirname(os.path.dirname(__file__))
logger.debug(f"Adding to sys.path: {project_root}")
sys.path.insert(0, project_root)

try:
    from api.app import app
    logger.debug("Flask app imported successfully.")
except Exception as e:
    logger.exception("Failed to import Flask app.")

application = app