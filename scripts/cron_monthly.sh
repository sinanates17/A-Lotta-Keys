#!/bin/bash

umask 000

PATH_THIS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PATH_THIS"
cd ..

set -o allexport
source .env
set +o allexport

source "$PATH_VENV/bin/activate"

pip list
python3 cron_monthly.py