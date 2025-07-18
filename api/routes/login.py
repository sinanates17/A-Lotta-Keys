from flask import Blueprint, jsonify, request, render_template, abort, current_app
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from datetime import datetime
from config import PATH_DATA, PATH_USERS, PATH_BEATMAPSETS
from utils import Helper
import json

login = Blueprint("login", __name__)