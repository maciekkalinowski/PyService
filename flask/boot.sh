#!/bin/bash
source venv/bin/activate

exec gunicorn -b :5000 --threads 4 --access-logfile - --error-logfile - run:app