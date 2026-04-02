#!/bin/bash
cd /home/zmx/.openclaw/workspace/tuoyue-erp/backend
source venv/bin/activate
export PYTHONUNBUFFERED=1
exec python manage.py runserver 0.0.0.0:8000
