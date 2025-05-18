#!/bin/bash

PATH_THIS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PATH_THIS"
cd ..

set -o allexport
source .env
set +o allexport

source "$PATH_VENV/bin/activate"

cd scripts
echo "$PATH_VENV"
echo "Python: $(which python)"
echo "pip: $(which pip)"
pip list
python3 cron_daily.py