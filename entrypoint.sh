#!/usr/bin/env bash
set -e
alembic upgrade head
python3 entrypoint.py
