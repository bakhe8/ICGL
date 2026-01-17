#!/usr/bin/env pwsh
<#!
.SYNOPSIS
    One-click ICGL server control (start/stop/restart/health)
.DESCRIPTION
    Starts/stops ICGL API server in background and can verify /health.
.EXAMPLE
    .\scripts\server.ps1
    .\scripts\server.ps1 -Action health
#>

param(
    [ValidateSet("start", "stop", "restart", "health")]
    [string]$Action = "restart",
    [switch]$NoHealthCheck
)

$ErrorActionPreference = "SilentlyContinue"

$projectRoot = Split-Path -Parent $PSScriptRoot
$srcPath = Join-Path $projectRoot "src"
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
$pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }
$pidFile = Join-Path $projectRoot "data\icgl_server.pid"
$lockFile = Join-Path $projectRoot "data\icgl.lock"

function Get-IcglProcess {
    if (Test-Path $pidFile) {
        $pid = Get-Content $pidFile -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($pid) {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                return $proc
            }
        }
    }

    return Get-Process -ErrorAction SilentlyContinue | Where-Object {
        ($_.ProcessName -eq "python") -and ($_.CommandLine -like "*uvicorn*icgl.api.server*" -or $_.CommandLine -like "*uvicorn*8000*")
    } | Select-Object -First 1
}

function Stop-IcglServer {
    # Stop any uvicorn server processes for ICGL
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*icgl.api.server*" -or $_.CommandLine -like "*uvicorn*8000*"
    } | ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }

    $proc = Get-IcglProcess
    if ($proc) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    if (Test-Path $pidFile) {
        Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
    }

    if (Test-Path $lockFile) {
        Remove-Item -LiteralPath $lockFile -Force -ErrorAction SilentlyContinue
    }
}

function Start-IcglServer {
    $existing = Get-IcglProcess
    if ($existing) {
        Write-Host "ℹ️  Server already running (PID $($existing.Id))" -ForegroundColor Gray
        return
    }
    if (Test-Path $lockFile) {
        Remove-Item -LiteralPath $lockFile -Force -ErrorAction SilentlyContinue
    }
    Push-Location $srcPath
    try {
        $proc = Start-Process $pythonCmd -ArgumentList "-m", "uvicorn", "icgl.api.server:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -WindowStyle Minimized -PassThru
        if ($proc -and $proc.Id) {
            $pidDir = Split-Path -Parent $pidFile
            if (-not (Test-Path $pidDir)) { New-Item -ItemType Directory -Path $pidDir | Out-Null }
            Set-Content -Path $pidFile -Value $proc.Id -Force
        }
    } finally {
        Pop-Location
    }
}

function Test-IcglHealth {
    $max = 10
    for ($i = 0; $i -lt $max; $i++) {
        try {
            $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:8000/health" -TimeoutSec 3
            if ($resp.StatusCode -eq 200) {
                Write-Host "✅ Health OK" -ForegroundColor Green
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    Write-Host "⚠️ Health check failed" -ForegroundColor Yellow
    return $false
}

switch ($Action) {
    "stop" {
        Stop-IcglServer
        Write-Host "⏹️  Server stopped" -ForegroundColor Yellow
    }
    "start" {
        $existing = Get-IcglProcess
        if ($existing) {
            Write-Host "ℹ️  Server already running (PID $($existing.Id))" -ForegroundColor Gray
        } else {
            Start-IcglServer
            Write-Host "🚀 Server started" -ForegroundColor Green
        }
        if (-not $NoHealthCheck) { Test-IcglHealth | Out-Null }
    }
    "restart" {
        Stop-IcglServer
        Start-Sleep -Seconds 1
        Start-IcglServer
        Write-Host "🔄 Server restarted" -ForegroundColor Green
        if (-not $NoHealthCheck) { Test-IcglHealth | Out-Null }
    }
    "health" {
        Test-IcglHealth | Out-Null
    }
}
