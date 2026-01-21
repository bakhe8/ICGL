#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Bootstrapping ICGL development environment..."

cd "$ROOT_DIR"

if command -v poetry >/dev/null 2>&1; then
  echo "Installing via poetry..."
  poetry install
else
  echo "Poetry not found — installing editable package via pip and requirements-dev.txt"
  python -m pip install --upgrade pip
  if [ -f requirements-dev.txt ]; then
    pip install -r requirements-dev.txt
  fi
  pip install -e .[dev] || true
fi

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install || true
else
  echo "pre-commit not found; skipping pre-commit install"
fi

echo "Bringing up Qdrant (docker-compose)..."
if command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d qdrant || true
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  docker compose up -d qdrant || true
else
  echo "Docker/compose not available — start Qdrant manually or via Dev Container"
fi

echo "Bootstrap complete."
