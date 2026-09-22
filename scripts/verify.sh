#!/usr/bin/env bash
set -euo pipefail

python3 -m compileall -q app.py
python3 -m pytest -q
