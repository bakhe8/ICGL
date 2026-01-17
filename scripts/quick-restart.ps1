#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick server restart - minimal output, background mode
.DESCRIPTION
    Fast restart for development workflow
#>

$ErrorActionPreference = "SilentlyContinue"

# Delegate to unified server script
$projectRoot = Split-Path -Parent $PSScriptRoot
$serverScript = Join-Path $projectRoot "scripts\server.ps1"

& $serverScript -Action restart -NoHealthCheck
