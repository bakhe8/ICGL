<#
.SYNOPSIS
Creates a Windows virtual environment using a specified Python interpreter
and installs development dependencies for the ICGL project.

USAGE (PowerShell):
  ./scripts/create_venv_windows.ps1
  ./scripts/create_venv_windows.ps1 -PythonPath 'C:\Python314\python.exe'

#>

param(
    [string]$PythonPath = 'C:\Python314\python.exe',
    [string]$VenvDir = '.venv'
)

Write-Output "Using Python: $PythonPath"

if (-not (Test-Path $PythonPath)) {
    Write-Error "Python executable not found at $PythonPath"
    exit 1
}

# Create venv
& $PythonPath -m venv $VenvDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtualenv using $PythonPath"
    exit $LASTEXITCODE
}

$ActivateScript = Join-Path $VenvDir 'Scripts\Activate.ps1'
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Activation script not found at $ActivateScript"
    exit 1
}

Write-Output "Activating venv..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. $ActivateScript

Write-Output "Upgrading pip and installing dev dependencies..."
python -m pip install --upgrade pip
python -m pip install -e .[dev] || python -m pip install -r requirements-dev.txt

Write-Output "Virtual environment ready. Activate with:`n    .\\.venv\\Scripts\\Activate.ps1"
Write-Output "Then run the API: python -m api.main"
