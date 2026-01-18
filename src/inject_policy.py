import requests
import json

BASE_URL = "http://127.0.0.1:8000"

payload = {
    "agent_id": "Policy_Guard",
    "proposal": "New Security Policy: Zero Trust",
    "status": "NEW",
    "requester": "CISO / Security Committee",
    "executive_brief": "تفعيل سياسة 'انعدام الثقة' (Zero Trust) على جميع نقاط الوصول. يتطلب التحقق المستمر من الهوية لكل طلب.",
    "impact": "✅ رفع مستوى الأمان للمستوى A+.\n📝 سيتم تسجيل كل عملية وصول في سجل التدقيق (Audit Log).\n⚠️ قد يلاحظ المستخدمون بطء طفيف (2ms).",
    "details": "عند الموافقة، سيقوم النظام بإنشاء ملف 'policy_audit.log' وتوثيق تفعيل السياسة فيه."
}

try:
    print("🚀 Injecting Policy Proposal...")
    response = requests.post(f"{BASE_URL}/proposals", json=payload)
    if response.status_code == 200:
        print("✅ Success! Policy injected.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
