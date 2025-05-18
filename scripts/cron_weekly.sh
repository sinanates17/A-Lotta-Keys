#!/bin/bash
PATH_THIS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PATH_THIS"
cd ..

set -o allexport
source .env
set +o allexport

source "$PATH_VENV/bin/activate"

python3 cron_daily.py

python3 cron_weekly.py