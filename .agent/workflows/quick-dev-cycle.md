---
description: Complete development cycle - code change + test
---

# Quick Development Cycle

Fast workflow for: make changes → restart server → verify

## Steps

// turbo-all

1. **Quick restart server**

```powershell
.\scripts\quick-restart.ps1
```

1. **Wait for startup**

```powershell
Start-Sleep -Seconds 4
```

1. **Health check**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET -ErrorAction SilentlyContinue
```

## Usage

Say: `/quick-dev-cycle` after making code changes
