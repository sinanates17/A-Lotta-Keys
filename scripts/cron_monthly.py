"""
This script and its children are meant to be run monthly.

Parent script: cron_monthly.py

Child script 1: monthly_stats_gross.py
    - Request EVERY ranked and loved mania map
        - Under the key of the current timestamp, extract the following into a dictionary for each keymode
            - Playcount
            - Passcount
            - Total ranked mapsets
            - Total ranked difficulties
            - Total ranked drain time
            - Total ranked hitobjects
    - Go through the past month of data and get lists of the most popular:
        - 9K+ beatmaps by playcount
    - Get newly ranked/loved 9K+ beatmaps

Child script 2: monthly_stats_fine.py
    - Go through every user.json to create lists of:
        - Most popular mappers by playcount
        - Most active players by # of new scores

"""

def main():
    pass

if __name__ == "__main__":
    main()