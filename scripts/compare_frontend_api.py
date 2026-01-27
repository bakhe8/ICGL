import json
import re
import urllib.request
from pathlib import Path

root = Path("frontend/web-app")
paths = set()
for p in root.rglob("*.ts*"):
    try:
        s = p.read_text(errors="ignore")
    except Exception:
        continue
    for m in re.finditer(r"['\"](/api[\w\-/_{}?=:.]*)['\"]", s):
        paths.add(m.group(1))

paths_norm = sorted({re.sub(r"\?.*$", "", pp) for pp in paths})

api_paths = None
try:
    resp = urllib.request.urlopen("http://127.0.0.1:8000/api/openapi.json", timeout=5)
    j = json.loads(resp.read().decode())
    api_paths = set(j.get("paths", {}).keys())
except Exception:
    api_paths = None

out = {"frontend_paths": paths_norm, "openapi_count": len(api_paths) if api_paths is not None else None}
if api_paths is not None:
    missing = [p for p in paths_norm if p not in api_paths and p.replace("/api", "") not in api_paths]
    out["missing"] = missing

print(json.dumps(out, ensure_ascii=False, indent=2))
