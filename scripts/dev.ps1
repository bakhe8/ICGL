$ErrorActionPreference = "Stop"

Write-Host "Starting ICGL dev stack (API + Vite)..." -ForegroundColor Cyan

# Paths
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Split-Path -Parent $root
$apiCmd = "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000"
$webDir = Join-Path $repo "web"
$viteCmd = "npm run dev -- --host --port 5173"

# Start API
Write-Host "-> API: $apiCmd" -ForegroundColor DarkGray
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$repo`"; $apiCmd" -WindowStyle Hidden

# Start Vite
Write-Host "-> Web: $viteCmd" -ForegroundColor DarkGray
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$webDir`"; $viteCmd" -WindowStyle Hidden

Write-Host "Servers launching in background:" -ForegroundColor Green
Write-Host "  API   -> http://localhost:8000" -ForegroundColor Green
Write-Host "  Front -> http://localhost:5173/dashboard" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop this wrapper. To stop child processes, close their windows or kill uvicorn/npm." -ForegroundColor Yellow
