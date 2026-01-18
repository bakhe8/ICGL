import requests
import json

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "agent_id": "DBA_Bot",
    "proposal": "Emergency Backup (Pre-Patch)",
    "status": "NEW",
    "requester": "Database Administrator Team",
    "executive_brief": "طلب نسخ احتياطي فوري لقاعدة البيانات قبل تطبيق التحديثات الأمنية العاجلة.",
    "impact": "✅ حماية البيانات من الفقدان (RPO = 0)\n⚠️ إيقاف الخدمة لمدة 30 ثانية أثناء النسخ (Lock Tables)",
    "details": "سيتم إنشاء نسخة كاملة (Full Dump) وحفظها في المسار الآمن مع ضغط البيانات."
}

try:
    print("🚀 Injecting Emergency Backup Proposal...")
    response = requests.post(f"{BASE_URL}/proposals", json=payload)
    if response.status_code == 200:
        print("✅ Success! Proposal injected.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
