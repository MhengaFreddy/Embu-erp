#!/bin/bash
# Force rebuild 2026-05-26
set -e
export FLASK_APP=run.py
python seed.py
exec python run.py