// دوال جلب البيانات الحية من النظام (API)

export async function fetchAgents() {
    const res = await fetch('/api/system/agents');
    if (!res.ok) throw new Error('فشل جلب الوكلاء');
    const data = await res.json();
    return data.agents;
}

export async function fetchAnalysis(adrId: string) {
    const res = await fetch(`/api/analysis/${adrId}`);
    if (!res.ok) throw new Error('فشل جلب التحليل');
    return await res.json();
}

export async function fetchEvents() {
    const res = await fetch('/api/events');
    if (!res.ok) throw new Error('فشل جلب سجل الأحداث');
    return await res.json();
}

export async function fetchStatus() {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error('فشل جلب حالة النظام');
    return await res.json();
}

export async function fetchIdeaSummary(adrId: string) {
    const res = await fetch(`/api/idea-summary/${adrId}`);
    if (!res.ok) throw new Error('فشل جلب ملخص الفكرة');
    return await res.json();
}
