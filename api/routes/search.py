from flask import Blueprint, jsonify, request
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import PATH_DATA
import json

search_bp = Blueprint("search", __name__)

def load_user_compact():
    with open(f"P{PATH_DATA}/users_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)
    return compact

def load_beatmap_compact():
    with open(f"P{PATH_DATA}/beatmaps_compact.json", "r", encoding="utf-8") as f:
        compact = json.load(f)
    return compact 

@search_bp.route("/users", methods=["GET"])
def get_users():
    filters = request.args
    users = load_user_compact()
    users = users["users"]

@search_bp.route("/beatmaps", methods=["GET"])
def get_beatmaps():
    filters = request.args
    beatmaps = load_beatmap_compact()
