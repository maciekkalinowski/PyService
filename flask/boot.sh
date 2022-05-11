#!/bin/bash
source venv/bin/activate

exec gunicorn -b :$PORT --threads 4 --access-logfile - --error-logfile - run:app