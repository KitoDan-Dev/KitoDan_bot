#!/usr/bin/env bash
set -euo pipefail

python3 -m venv server/.venv
server/.venv/bin/pip install -r server/requirements.txt

cd client
npm install
