#! /usr/bin/env bash
set -e

python /app/app/celeryworker_pre_start.py

celery worker -A app.worker -l info -Q main-queue -c 1 --pool=solo
#celery worker -A app.workers.summarizer -l info -Q summarize-queue -c 10
