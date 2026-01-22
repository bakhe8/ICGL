# تقرير وكلاء ICGL - الجزء 2: مصفوفة التكامل بين الوكلاء

| الوكيل            | يتكامل مع                | نوع التكامل/الاعتمادية                |
|-------------------|-------------------------|---------------------------------------|
| ArchitectAgent    | Builder, Engineer       | يزودهم بسياق التصميم والتحليل         |
| PolicyAgent       | Guardian, Sentinel      | يفرض السياسات ويكشف الانتهاكات        |
| FailureAgent      | Sentinel, Builder       | يزودهم بتحذيرات حول نقاط الفشل        |
| SentinelAgent     | Policy, Failure         | يراقب المخاطر ويرسل إشارات            |
| GuardianAgent     | Policy, Architect       | يحمي المفاهيم ويمنع انتهاك المبادئ    |
| BuilderAgent      | Architect, Engineer     | ينفذ توصيات التصميم ويولد الكود        |
| EngineerAgent     | Builder, Policy         | ينفذ التغييرات ويراعي السياسات        |
| MediatorAgent     | جميع الوكلاء            | يحل النزاعات ويبني توافق              |
| DocumentationAgent| Builder, Engineer       | يوثق التغييرات ويحلل جودة الوثائق     |
| Specialists       | جميع الوكلاء            | يقدم استشارات تخصصية عند الحاجة       |
| AgentRegistry     | جميع الوكلاء            | يدير دورة الحياة والتنسيق             |
| Agent Base        | جميع الوكلاء            | يوفر الأساس البرمجي                   |
| CapabilityChecker | جميع الوكلاء            | يكشف الفجوات ويمنع التكرار            |
| RefactoringAgent  | Builder, Engineer       | يحسن جودة الكود ويقترح تحسينات        |
| VerificationAgent | Builder, Testing        | يتحقق من جودة الكود والاختبارات        |
| TestingAgent      | Builder, Engineer       | يولد وينفذ اختبارات                   |
