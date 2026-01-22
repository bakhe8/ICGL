# `03-System-Spec.md`  
**النموذج التقني الصلب (Core System Specification)**

هذا الملف هو المرجع التنفيذي الذي يمكن لفريق تطوير أن يبدأ منه مباشرة.  
لا يحتوي فلسفة ولا سردًا، بل يترجم المبادئ إلى بنية تقنية صلبة.

---

## 1. نموذج البيانات (Postgres – MVP)

### 1.1 الجداول الأساسية

```sql
workspaces
- id (uuid, pk)
- name (text)
- mode (enum: NORMAL, SANDBOX, JOURNAL)
- created_at

nodes
- id (uuid, pk)
- workspace_id (uuid, fk)
- type (enum: IDEA, PROPOSAL, DECISION, CONFLICT, EXPERIMENT, NOTE, JOURNAL_ENTRY)
- state (enum: RAW, OPEN, IN_REVIEW, APPROVED, REJECTED, DORMANT, ARCHIVED, FROZEN)
- title (text)
- content_md (text)
- visibility (enum: PRIVATE, SHARED)
- created_by (text/uuid)
- created_at
- updated_at

node_versions
- id (uuid, pk)
- node_id (uuid, fk)
- version_no (int)
- content_md (text)
- diff_summary (text, nullable)
- created_at

edges
- id (uuid, pk)
- from_node_id (uuid, fk)
- to_node_id (uuid, fk)
- type (enum: DERIVED_FROM, EVOLVED_INTO, REFERENCES, SUPPORTS, BLOCKS, CONFLICTS_WITH, QUESTIONS)
- created_at

agents
- id (uuid, pk)
- key (text unique)  -- architect, risk, explorer...
- display_name (text)
- scope (jsonb)
- enabled (bool)
- created_at

agent_runs
- id (uuid, pk)
- agent_id (uuid, fk)
- node_id (uuid, fk)
- mode (enum: NORMAL, SANDBOX, RED_TEAM)
- status (enum: QUEUED, RUNNING, DONE, FAILED)
- input_snapshot (jsonb)
- output (jsonb)
- created_at
- finished_at

proposals
- node_id (uuid, pk, fk -> nodes.id)  -- type = PROPOSAL
- trigger (text)
- impact (text)
- risks (jsonb array)
- alternatives (jsonb array)
- effort_estimate (jsonb)
- execution_plan (text)

decisions
- node_id (uuid, pk, fk -> nodes.id)  -- type = DECISION
- proposal_node_id (uuid, fk)
- approved_by (text/uuid)
- approval_token (text unique)
- rationale (text)
- scope_guard (jsonb)
- created_at

conflicts
- node_id (uuid, pk, fk -> nodes.id)  -- type = CONFLICT
- left_proposal_id (uuid)
- right_proposal_id (uuid)
- summary (text)
- status (enum: OPEN, RESOLVED, ARCHIVED)

events
- id (uuid, pk)
- ts (timestamp)
- actor_type (enum: HUMAN, AGENT, SYSTEM)
- actor_id (text/uuid)
- event_type (text)
- entity_type (text)
- entity_id (uuid)
- payload (jsonb)
```

---

## 2. القيود السيادية (Sovereignty Constraints)

1. لا تنفيذ دون قرار:
   - أي عملية تنفيذ تتطلب:
     - وجود Node من نوع `DECISION`
     - حالته `APPROVED`
     - `approval_token` صالح

2. مفتاح الاعتماد (Approval Token):
   - هو مفتاح تقني فعلي.
   - بدونه لا يمكن لمحرك التنفيذ الوصول للملفات أو توليد مخرجات.

3. Scope Guard:
   - كل قرار يحمل `scope_guard`
   - يحدد:
     - المسموح
     - الممنوع
   - أي تنفيذ خارج النطاق يُرفض آليًا ويُسجل كحدث أمني.

---

## 3. أنواع الأحداث (Event Types)

أمثلة:

- `NODE_CREATED`
- `STATE_CHANGED`
- `AGENT_RUN_STARTED`
- `AGENT_RUN_DONE`
- `PROPOSAL_CREATED`
- `CONFLICT_DETECTED`
- `DECISION_APPROVED`
- `EXECUTION_STARTED`
- `EXECUTION_RESULT`
- `EXECUTION_BLOCKED`

كل حدث يُسجل في جدول `events` مع:

```json
{
  "actor_type": "HUMAN | AGENT | SYSTEM",
  "event_type": "DECISION_APPROVED",
  "entity_type": "decision",
  "entity_id": "uuid",
  "payload": { }
}
```

---

## 4. واجهات API الأساسية (MVP)

```
POST   /workspaces
GET    /workspaces

POST   /nodes
GET    /nodes
GET    /nodes/{id}
POST   /nodes/{id}/versions

POST   /edges

POST   /agents/{agent_key}/run?node_id=...

POST   /conflicts/detect?node_id=...

POST   /decisions/approve
  body: { proposal_node_id, approved_by }

POST   /execute
  body: { decision_id, approval_token }

GET    /timeline
GET    /metrics/dashboard
```

---

## 5. قواعد Sandbox وJournal

- `workspace.mode = SANDBOX`
  - لا يسمح بترقية أي محتوى إلى مسار رسمي.
  - كل ما فيه معزول.

- `workspace.mode = JOURNAL`
  - كل Nodes افتراضيًا `PRIVATE`.
  - لا تدخل في تحليل الوكلاء إلا بطلب صريح.
  - عند الطلب:
    - يسمح فقط بالاطلاع على ما شارك المستخدم في بنائه أو كتابته.
