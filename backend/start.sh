#!/bin/bash
set -e
export FLASK_APP=run.py
python seed.py
exec python run.py