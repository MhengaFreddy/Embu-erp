#!/bin/bash
set -e
flask db upgrade
python seed.py
exec python run.py