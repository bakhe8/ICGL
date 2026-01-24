import time

import requests

url = "http://127.0.0.1:8000/api/nexus/consult"
payload = {
    "agent_role": "sentinel",
    "problem_title": "Network Reliability Audit",
    "problem_context": "The system is experiencing high latency. Is there any network congestion or connectivity issues? Please audit the system state.",
}

try:
    print("🚀 Triggering Expansion Protocol via Sentinel...")
    response = requests.post(url, json=payload, timeout=90)
    data = response.json()

    print("\nAGENT ANALYSIS:")
    print("-" * 50)
    print(data.get("analysis", "NO ANALYSIS FOUND"))

    # Check if expansion was logged (by checking secretary logs)
    print("\n🔍 Checking Secretary Logs for Growth Alerts...")
    time.sleep(2)
    logs_url = "http://127.0.0.1:8000/api/system/secretary-logs"
    logs_res = requests.get(logs_url)
    logs_data = logs_res.json()

    alerts = [
        log
        for log in logs_data.get("logs", [])
        if "GROWTH" in log.get("event", "").upper()
        or "SOVEREIGN" in log.get("summary", "").upper()
    ]
    if alerts:
        print("\n✅ SUCCESS: Sovereign Growth Alert Detected!")
        for alert in alerts:
            print(f"  - [{alert['timestamp']}] {alert['summary']}")
    else:
        print("\n⚠️ No growth alerts detected in recent logs.")

except Exception as e:
    print(f"FAILED: {e}")
