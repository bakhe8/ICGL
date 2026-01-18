# Runs a quick pytest smoke in the current repo.
# Usage: powershell -File scripts/run_smoke_tests.ps1

$ErrorActionPreference = "Stop"

Write-Host "Activating venv and running pytest..." -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    Write-Host "Virtualenv not found. Installing dependencies via Poetry..." -ForegroundColor Yellow
    poetry install --no-interaction
}

poetry run pytest -q --disable-warnings --maxfail=1
