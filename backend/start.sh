#!/bin/bash
set -e
export FLASK_APP=run.py
flask db upgrade
python seed.py
exec python run.py