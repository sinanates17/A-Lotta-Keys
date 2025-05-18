#!/bin/bash
set -o allexport
source ../.env
set +o allexport

source "$PATH_VENV/bin/activate"

python3 cron_monthly.py