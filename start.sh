#!/usr/bin/env bash
set -euo pipefail

if [[ -f "venv311/Scripts/activate" ]]; then
  # shellcheck disable=SC1091
  source "venv311/Scripts/activate"
else
  echo "ERROR: venv not found at venv311/Scripts/activate"
  exit 1
fi

echo "Using python: $(command -v python)"
python --version || true

cleanup() {
  echo
  echo "Stopping dev servers..."
  jobs -pr | xargs -r kill
}
trap cleanup INT TERM EXIT

# server
uvicorn services.predictions_api:app --reload --port 8000 &

# client
npm run dev &

wait
