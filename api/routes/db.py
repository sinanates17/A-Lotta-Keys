import sqlite3
from flask import g
import sys
from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PATH_DATA

DATABASE = Path(f"{PATH_DATA}/profiles.sqlite")
def get_pf_db():
    if "pf_db" not in g:
        g.pf_db = sqlite3.connect(DATABASE)
        g.pf_db.execute("PRAGMA journal_mode=WAL;")
        g.pf_db.row_factory = sqlite3.Row
    return g.pf_db

def get_pf_db_bot():
    pf_db = sqlite3.connect(DATABASE)
    pf_db.execute("PRAGMA journal_mode=WAL;")
    pf_db.row_factory = sqlite3.Row
    return pf_db
