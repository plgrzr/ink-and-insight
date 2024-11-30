#!/bin/bash
export FLASK_APP=run.py
export FLASK_ENV=production
gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 4 "app:create_app()" 