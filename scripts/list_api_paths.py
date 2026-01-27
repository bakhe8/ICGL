# Ensure project root is on sys.path so `backend` package is importable
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from typing import cast

from fastapi import FastAPI
from fastapi.routing import Mount

from backend.api import server as s

api_mount = None
# s.app may be an ASGI app; guard and cast to FastAPI to access .routes safely
if hasattr(s, "app") and hasattr(s.app, "routes"):
    for r in cast(FastAPI, s.app).routes:
        if isinstance(r, Mount) and r.path == "/api":
            api_mount = r
            break

paths = []
if api_mount:
    subapp = api_mount.app
    paths = sorted({("/api" + rr.path).replace("//", "/") for rr in subapp.routes})

print(json.dumps({"count": len(paths), "paths": paths}, ensure_ascii=False, indent=2))
