from ossapi import ossapi, Ossapi
from dotenv import load_dotenv
from datetime import datetime
from config import OSU_API_ID, OSU_API_SECRET, OSU_API_VERSION, DEBUG
import utils
import os

def main():
    osu_api = Ossapi(client_id=OSU_API_ID, client_secret=OSU_API_SECRET, api_version=OSU_API_VERSION)


if __name__ == "__main__":
    main()

