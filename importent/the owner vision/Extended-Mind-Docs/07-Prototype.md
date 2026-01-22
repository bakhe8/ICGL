# `07-Prototype.md`  
**النماذج الأولية للواجهة (Wireframes & UX Skeleton)**

هذا الملف لا يشرح “لماذا”، بل يوضح “كيف يبدو النظام أثناء الاستخدام”.  
هو تمثيل بصري مبسط لتجربة العمل داخل العقل الممتد.

---

## 1. شاشة لوحة العمل (Workspace Home)

```
┌──────────────────────────────────────────────────────────────┐
│ Extended Mind │ Workspace: Project Alpha   [Mode: NORMAL]   │
├──────────────────────────────────────────────────────────────┤
│ [+ New Idea] [+ New Note] [+ Journal Entry] [Search…]       │
├──────────────────────────────────────────────────────────────┤
│ Left Panel (Graph/Tree)        │ Main Panel                  │
│ ┌───────────────────────────┐ │ ┌────────────────────────┐ │
│ │ Ideas                     │ │ │ Selected Node          │ │
│ │ - API redesign (OPEN)     │ │ │ Title                  │ │
│ │ - Printing rules (DORM)   │ │ │ Content (Markdown)     │ │
│ │ Conflicts                 │ │ │ Versions               │ │
│ │ - Perf vs Security (OPEN) │ │ │ Links                  │ │
│ └───────────────────────────┘ │ └────────────────────────┘ │
│                               │ [Run Agents] [Detect Conflict] │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. شاشة فكرة + تشغيل الوكلاء

```
┌──────────────────────────────────────────────────────────────┐
│ Idea: "API redesign"   State: OPEN   [Convert → Proposal]  │
├──────────────────────────────────────────────────────────────┤
│ Content (Markdown Editor)                                  │
│ ---------------------------------------------------------- │
│ ...                                                        │
├──────────────────────────────────────────────────────────────┤
│ Agents                                                     │
│ [Run Architect] [Run Risk] [Run Explorer] [Run All]        │
├──────────────────────────────────────────────────────────────┤
│ Suggestions / Outputs                                      │
│ ┌────────────────────────────┐ ┌─────────────────────────┐ │
│ │ Architect Proposal #12      │ │ Risk Notes #7           │ │
│ │ Impact.. Risks.. Alt..      │ │ Top risks.. mitigations │ │
│ └────────────────────────────┘ └─────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. شاشة قالب الاقتراح المنضبط

```
┌──────────────────────────────────────────────────────────────┐
│ Proposal (from Idea #...)                                  │
├──────────────────────────────────────────────────────────────┤
│ Trigger:   [............................................] │
│ Impact:    [............................................] │
│ Risks:     [+ Add Risk] (likelihood/severity/mitigation)  │
│ Alternatives: [+ Add Alt] (tradeoffs/why not)             │
│ Effort:   (S/M/L) hours: [min] - [max]                    │
│ Execution Plan: [........................................] │
├──────────────────────────────────────────────────────────────┤
│ [Save Draft]   [Submit for Decision]                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. شاشة التعارض (Conflict Case)

```
┌──────────────────────────────────────────────────────────────┐
│ Conflict Case: "Perf vs Security"   Status: OPEN           │
├──────────────────────────────────────────────────────────────┤
│ Left Proposal (Performance)        │ Right (Security)      │
│ ┌───────────────────────────────┐ │ ┌───────────────────┐ │
│ │ Claims: reduce latency         │ │ │ Claims: add checks│ │
│ │ Cost: medium                   │ │ │ Cost: high        │ │
│ └───────────────────────────────┘ │ └───────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│ System summary: what differs + what’s shared               │
│ Dimensions: [performance] [security] [maintainability]     │
├──────────────────────────────────────────────────────────────┤
│ [Ask another Agent] [Open Experiment Sandbox]              │
│ [Resolve: Choose Left] [Choose Right] [Defer]              │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. شاشة اعتماد القرار + Token

```
┌──────────────────────────────────────────────────────────────┐
│ Decision Approval                                          │
├──────────────────────────────────────────────────────────────┤
│ Proposal: #12 "API redesign plan"                          │
│ Rationale (why we choose it): [..........................] │
│ Scope Guard:                                                │
│  - Allowed: files/services/modules ...                      │
│  - Forbidden: touching auth/payment/...                     │
├──────────────────────────────────────────────────────────────┤
│ [Approve Decision] → generates Approval Token              │
│ Token: EM-APPROVE-9F3A-... (copy)                           │
│ [Run Execution Engine] (requires token)                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 6. شاشة لوحة المؤشرات (Metrics)

```
┌──────────────────────────────────────────────────────────────┐
│ Metrics Dashboard                                          │
├──────────────────────────────────────────────────────────────┤
│ Cognitive KPIs:                                            │
│ - Decision Clarity: 0.82 (target ≥0.80)                    │
│ - Healthy Conflict Density: 0.21 (target 0.15–0.35)        │
│ - Unknowns Captured Index: 2.4                             │
│                                                            │
│ Efficiency KPIs:                                           │
│ - Decision→Execution Lead Time: 1.8 days                   │
│ - Rollback/Regret Rate: 0.09                               │
└──────────────────────────────────────────────────────────────┘
```
