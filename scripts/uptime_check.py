"""
Simple uptime check with optional webhook alert.
Usage:
    python scripts/uptime_check.py --url http://127.0.0.1:8000/dashboard/overview --webhook https://example.com/hook
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error


def check(url: str, timeout: float = 5.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except urllib.error.URLError:
        return False


def notify(webhook: str, message: str) -> None:
    data = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5.0):
            pass
    except Exception as e:
        print(f"[alert] failed to send webhook: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Uptime check for ICGL API.")
    parser.add_argument("--url", required=True, help="URL to check (e.g., http://127.0.0.1:8000/health)")
    parser.add_argument("--webhook", help="Optional webhook for alerts (POST with JSON {text})")
    parser.add_argument("--retries", type=int, default=1, help="Retries on failure")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep between retries (seconds)")
    args = parser.parse_args()

    success = False
    for attempt in range(1, args.retries + 1):
        if check(args.url):
            success = True
            print(f"[ok] {args.url} reachable")
            break
        print(f"[warn] attempt {attempt} failed", file=sys.stderr)
        time.sleep(args.sleep)

    if not success:
        msg = f"ICGL API down: {args.url}"
        print(f"[alert] {msg}", file=sys.stderr)
        if args.webhook:
            notify(args.webhook, msg)


if __name__ == "__main__":
    main()
