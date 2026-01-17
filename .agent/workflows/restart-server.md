---
description: Restart the Python API server after code changes
---

# Restart ICGL API Server

This workflow automatically restarts the Python backend server after code changes.

## Steps

// turbo-all

1. **Find and stop the running server**

```powershell
Get-Process | Where-Object {$_.Path -like "*uvicorn*" -or ($_.CommandLine -like "*uvicorn*" -and $_.ProcessName -eq "python")} | Stop-Process -Force
```

1. **Wait for port to be released**

```powershell
Start-Sleep -Seconds 2
```

1. **Start the server with auto-reload**

```powershell
cd c:\Users\Bakheet\Documents\Projects\ICGL\src
python -m uvicorn icgl.api.server:app --host 127.0.0.1 --port 8000 --reload
```

## Usage

Just say: `/restart-server` and I'll execute this automatically.
