import React from 'react';

type Capability = {
  title: string;
  description: string;
  bullets: string[];
  tags: string[];
};

const capabilityGroups: { title: string; items: Capability[] }[] = [
  {
    title: 'الهندسة وتجربة المستخدم',
    items: [
      {
        title: 'واجهات حديثة',
        description: 'صفحات تفاعلية تُبنى بمكوّنات قابلة لإعادة الاستخدام وتناسب RTL.',
        bullets: ['React + TypeScript، تصميم نظيف.', 'ربط API وإدارة حالة خفيفة.', 'تنسيق المحتوى في بطاقات واضحة.'],
        tags: ['React', 'TypeScript', 'UX/UI'],
      },
      {
        title: 'صفحات محتوى',
        description: 'بناء صفحات تعريفية مثل القدرات التقنية مع قابلية الإثراء.',
        bullets: ['تقسيم المحتوى إلى أقسام وبطاقات.', 'إضافة CTA وروابط مساعدة بسهولة.', 'دعم ترجمة/RTL افتراضي.'],
        tags: ['Content', 'IA'],
      },
    ],
  },
  {
    title: 'البيانات والذكاء الاصطناعي',
    items: [
      {
        title: 'تحليل البيانات',
        description: 'تحضير وتحليل البيانات مع تقارير قابلة للتنفيذ.',
        bullets: ['Python + Pandas للـ EDA', 'لوحات بسيطة لعرض النتائج', 'تهيئة خطوط بيانات صغيرة'],
        tags: ['Python', 'EDA'],
      },
      {
        title: 'نماذج ML/NLP',
        description: 'نماذج خفيفة للتصنيف/التنبؤ أو استخدام Embeddings جاهزة.',
        bullets: ['scikit-learn للنماذج الكلاسيكية', 'دمج نماذج جاهزة عند الحاجة', 'تحسين تدريجي بعد الاختبار'],
        tags: ['ML', 'NLP', 'Embeddings'],
      },
    ],
  },
  {
    title: 'السحابة والعمليات',
    items: [
      {
        title: 'خدمات مصغّرة',
        description: 'نشر خدمات صغيرة قابلة للتوسع على السحابة.',
        bullets: ['FastAPI لواجهات REST', 'تجهيز CI/CD بسيط', 'استعمال AWS/Azure/GCP خفيف'],
        tags: ['Cloud', 'FastAPI', 'CI/CD'],
      },
      {
        title: 'أمن وموثوقية',
        description: 'حماية المفاتيح ومراقبة التشغيل الأولية.',
        bullets: ['حفظ الأسرار (.env)', 'تنبيهات وتحذيرات أساسية', 'اختبارات تشغيل سريعة'],
        tags: ['Security', 'Ops'],
      },
    ],
  },
];

const Badge = ({ label }: { label: string }) => (
  <span className="px-2 py-1 rounded-full text-[11px] bg-slate-100 text-slate-700 border border-slate-200">
    {label}
  </span>
);

const pathMappings = [
  { route: '/app/capabilities', file: 'web/src/components/TechnicalCapabilities.tsx' },
  { route: '/capabilities', file: 'web/src/components/TechnicalCapabilities.tsx' },
];

const TechnicalCapabilities: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs text-slate-500">القدرات التقنية</p>
        <h1 className="text-2xl font-semibold text-ink">صفحة القدرات التقنية</h1>
        <p className="text-sm text-slate-600 mt-1">
          ملخص لأهم المهارات والخدمات، مقسمة إلى محاور واضحة مع نقاط تنفيذية.
        </p>
      </div>

      <div className="space-y-5">
        {capabilityGroups.map((group) => (
          <div key={group.title} className="space-y-3">
            <h2 className="text-lg font-semibold text-ink">{group.title}</h2>
            <div className="grid gap-3 md:grid-cols-2">
              {group.items.map((cap) => (
                <div
                  key={cap.title}
                  className="rounded-xl border border-slate-200 bg-white/80 p-4 shadow-sm space-y-2"
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-base font-semibold text-ink">{cap.title}</h3>
                    <div className="flex gap-1 flex-wrap">
                      {cap.tags.map((t) => (
                        <Badge key={t} label={t} />
                      ))}
                    </div>
                  </div>
                  <p className="text-sm text-slate-600">{cap.description}</p>
                  <ul className="list-disc list-inside text-sm text-slate-700 space-y-1">
                    {cap.bullets.map((b) => (
                      <li key={b}>{b}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white/80 p-4 shadow-sm space-y-3">
        <h2 className="text-lg font-semibold text-ink">المسارات والملفات المستهدفة</h2>
        <p className="text-sm text-slate-600">
          هذه هي الروابط التي يفهمها النظام ومسارات الملفات التي يكتب فيها تلقائياً.
        </p>
        <ul className="space-y-2 text-sm text-slate-700">
          {pathMappings.map((item) => (
            <li key={item.route} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
              <div className="font-mono text-blue-700">{item.route}</div>
              <div className="text-xs text-slate-600">{item.file}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TechnicalCapabilities;
