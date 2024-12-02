#!/bin/bash
export FLASK_APP=run.py
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:${PORT:-5001} --workers 4 "app:create_app()"   --timeout 2000