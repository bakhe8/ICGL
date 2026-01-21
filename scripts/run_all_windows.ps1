<#
Runs a full local dev bootstrap on Windows (PowerShell).
This script will:
- fetch and checkout the `chore/editor-integration` branch
- set execution policy for the session
- build the `icgl` Docker image
- start Qdrant via docker compose
- rename any existing `icgl-app` container then run a new one
- (optionally) build the web UI if Node is available

Usage (PowerShell, run as normal user):
  cd C:\path\to\icgl
  .\scripts\run_all_windows.ps1

Note: This script assumes Docker Desktop is installed and running.
#>

Param()

function Exec {
    param([string]$cmd)
    Write-Host "-> $cmd" -ForegroundColor Cyan
    iex $cmd
}

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)\..\
$root = Get-Location
Write-Host "Project root: $root"

# Ensure branch
Exec "git fetch origin"
try {
    Exec "git checkout chore/editor-integration"
} catch {
    Exec "git checkout -b chore/editor-integration origin/chore/editor-integration"
}
Exec "git pull"

# Allow script execution for this user
try { Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force } catch {}

# Build image
Exec "docker build -t icgl:latest ."

# Start Qdrant
Exec "docker compose -f docker-compose.yml up -d qdrant"

# Rename existing container if present
$existing = (docker ps -a --filter name=icgl-app --format '{{.ID}}') -join ''
if ($existing) {
    Write-Host "Found existing icgl-app container ($existing). Renaming to icgl-app-old" -ForegroundColor Yellow
    try { Exec "docker rename icgl-app icgl-app-old" } catch {}
}

# Run new container
Exec "docker run -d --name icgl-app --env-file .env -p 3893:3893 icgl:latest"

# Show status and logs
Exec "docker ps --filter name=icgl-app"
Exec "docker ps --filter name=qdrant"
Exec "docker logs --tail 200 icgl-app"

# Optional: build web UI if node available
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "Building web UI..." -ForegroundColor Green
    Exec "cd web; npm install; npm run build; cd -"
} else {
    Write-Host "npm not found; skipping web build" -ForegroundColor Yellow
}

Write-Host "Bootstrap script finished. Check http://127.0.0.1:3893/ and http://127.0.0.1:6333/" -ForegroundColor Green
