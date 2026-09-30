#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACK_PID=$!
(cd frontend && npm run dev) &
FRONT_PID=$!
trap 'kill $BACK_PID $FRONT_PID 2>/dev/null || true' EXIT
wait
