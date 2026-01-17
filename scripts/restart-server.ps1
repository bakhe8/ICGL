#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Restarts the ICGL API server gracefully
.DESCRIPTION
    Stops any running uvicorn processes and starts a fresh server with auto-reload
.EXAMPLE
    .\restart-server.ps1
#>

param(
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

Write-Host "🔄 Restarting ICGL API Server..." -ForegroundColor Cyan

# 1. Find and stop running server
Write-Host "  ⏹️  Stopping existing server..." -ForegroundColor Yellow

$processes = Get-Process -ErrorAction SilentlyContinue | Where-Object {
    ($_.ProcessName -eq "python") -and 
    ($_.Path -like "*python.exe") -and
    ($_.CommandLine -like "*uvicorn*icgl.api.server*" -or $_.CommandLine -like "*uvicorn*8000*")
}

if ($processes) {
    $processes | ForEach-Object {
        Write-Host "    Stopping process $($_.Id)..." -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force
    }
    Write-Host "  ✅ Server stopped" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  No running server found" -ForegroundColor Gray
}

# 2. Wait for port to be released
Write-Host "  ⏳ Waiting for port 8000 to be released..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# 3. Check if port is really free
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "  ⚠️  Port 8000 still in use. Waiting 3 more seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# 4. Start the server
Write-Host "  🚀 Starting server with auto-reload..." -ForegroundColor Yellow

$projectRoot = Split-Path -Parent $PSScriptRoot
$srcPath = Join-Path $projectRoot "src"

Push-Location $srcPath
try {
    Write-Host "  📂 Working directory: $srcPath" -ForegroundColor Gray
    Write-Host "  🌐 Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "`n" -NoNewline
    
    # Start in background if -Force, otherwise foreground
    if ($Force) {
        Start-Process python -ArgumentList "-m", "uvicorn", "icgl.api.server:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Host "✅ Server started in background" -ForegroundColor Green
    } else {
        python -m uvicorn icgl.api.server:app --host 127.0.0.1 --port 8000 --reload
    }
} finally {
    Pop-Location
}
