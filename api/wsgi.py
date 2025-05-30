import sys
import os

project_home = os.path.dirname(__file__)
sys.path.insert(0, project_home)

from app import app

application = app 