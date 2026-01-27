#!/usr/bin/env python3
import json
import sys
from urllib.request import urlopen


def main():
    url = "http://127.0.0.1:8000/api/openapi.json"
    try:
        data = urlopen(url, timeout=5).read()
        spec = json.loads(data)
    except Exception as e:
        print("ERROR_FETCH", e)
        return 2

    paths = spec.get("paths", {})
    missing = []
    for path, ops in paths.items():
        for method, op in ops.items():
            responses = op.get("responses", {})
            ok = responses.get("200") or responses.get("201") or responses.get("default")
            has_schema = False
            if ok:
                content = ok.get("content", {})
                appjson = content.get("application/json")
                if appjson:
                    schema = appjson.get("schema")
                    if schema:
                        if "$ref" in schema:
                            has_schema = True
                        elif schema.get("type") == "object" and schema.get("properties"):
                            has_schema = True
                        elif schema.get("type") == "array" and schema.get("items"):
                            items = schema.get("items")
                            if "$ref" in items or items.get("properties"):
                                has_schema = True
            if not has_schema:
                missing.append(
                    {"path": path, "method": method, "operationId": op.get("operationId"), "summary": op.get("summary")}
                )

    out = {
        "missing_count": len(missing),
        "missing": missing,
        "components": list(spec.get("components", {}).get("schemas", {}).keys()),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
