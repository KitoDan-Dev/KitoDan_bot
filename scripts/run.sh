#!/usr/bin/env bash
set -euo pipefail

server/.venv/bin/python -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000 &
cd client
npm run dev -- --host 0.0.0.0 --port 5173
