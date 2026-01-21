#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Ensuring qdrant is up..."
docker compose -f docker-compose.yml up -d qdrant || true

EXIST=$(docker ps -a --filter "name=icgl-app" --format '{{.ID}}')
if [ -n "$EXIST" ]; then
  echo "Found existing container icgl-app ($EXIST). Stopping and removing..."
  docker rm -f icgl-app
fi

echo "Starting icgl service (compose)..."
docker compose -f docker-compose.yml up -d --build icgl

echo "Done. Run: docker ps --filter name=icgl-app"
