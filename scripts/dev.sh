#!/usr/bin/env bash
# Author : Shantanu Zadbuke
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v docker >/dev/null 2>&1; then
  true
else
  echo "Docker is required. Please install Docker Desktop." >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  docker compose up --build -d
else
  docker-compose up --build -d
fi

echo "App running at http://127.0.0.1:${PORT:-8080}/ (docs at /docs)"


