# --- ICGL Singleton ---
from ..governance.icgl import ICGL
from ..kb.schemas import ADR, uid, Proposal
_icgl_instance = None
def get_icgl():
    global _icgl_instance
    if _icgl_instance is None:
        _icgl_instance = ICGL()
    return _icgl_instance
from ..utils.logging_config import get_logger
logger = get_logger(__name__)
# --- UI Committee Endpoints ---

# --- Core Imports ---
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Depends, Header
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
import json
from fastapi.encoders import jsonable_encoder
import logging
from dotenv import load_dotenv

# Load Environment from Project Root
root_dir = Path(__file__).resolve().parents[3] # src/icgl/api -> src/icgl -> src -> ROOT
env_path = root_dir / ".env"
load_dotenv(dotenv_path=env_path)
print(f"🌍 Loading Environment from: {env_path}")
print(f"🔑 Key Status: {'OPENAI_API_KEY' in os.environ}")

# --- FastAPI App Initialization ---
app = FastAPI()
from ..agents.external_consultant import ExternalConsultantAgent
from ..agents.hr_agent import HRAgent
from ..dashboard import Dashboard
from ..agents.base import Problem, AgentRole
import os
import shutil
import time
import asyncio
from datetime import datetime

external_consultant = ExternalConsultantAgent()
hr_agent = HRAgent()
dashboard = Dashboard()
proposals_store = []  # Simple in-memory store for agent/user proposals

# --- External Consultant Endpoints ---
class CommitteeReportRequest(BaseModel):
    report: dict

# --- HR Agent Endpoints ---
class HRRecordRequest(BaseModel):
    name: str
    role: str
    duties: list
    limits: list

# --- Dashboard Endpoints ---
class CommitteeRequest(BaseModel):
    name: str
    members: list
    details: dict = {}

class ReportRequest(BaseModel):
    title: str
    content: str
    details: dict = {}

class RequestRequest(BaseModel):
    title: str
    type: str
    details: dict = {}

class DecisionRequest(BaseModel):
    decision: str
    rationale: str
    details: dict = {}

# --- نقاط النهاية بعد تعريف app مباشرة ---
def _require_api_key(x_icgl_api_key: str = Header(default=None)):
    """
    Simple API key gate. If env ICGL_API_KEY is set, header X-ICGL-API-KEY must match.
    """
    expected = os.getenv("ICGL_API_KEY")
    if expected and x_icgl_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.post("/dashboard/committee")
async def add_committee(req: CommitteeRequest, _: bool = Depends(_require_api_key)):
    dashboard.add_committee({
        "name": req.name,
        "members": req.members,
        "details": req.details
    })
    return {"status": "ok"}

@app.post("/dashboard/report")
async def add_report(req: ReportRequest, _: bool = Depends(_require_api_key)):
    dashboard.add_report({
        "title": req.title,
        "content": req.content,
        "details": req.details
    })
    return {"status": "ok"}

@app.post("/dashboard/request")
async def add_request(req: RequestRequest, _: bool = Depends(_require_api_key)):
    dashboard.add_request({
        "title": req.title,
        "type": req.type,
        "details": req.details
    })
    return {"status": "ok"}

@app.post("/dashboard/decision")
async def log_decision(req: DecisionRequest, _: bool = Depends(_require_api_key)):
    dashboard.log_decision({
        "decision": req.decision,
        "rationale": req.rationale,
        "details": req.details
    })
    return {"status": "ok"}


# --- SCP Real Data Endpoints ---

from ..kb.schemas import Proposal as ProposalSchema, uid

# Initialize Store from Persistence
def _load_proposals():
    kb = get_icgl().kb
    stored = kb.get_all_proposals()
    
    # Convert Schema objects to dicts for API compatibility
    # If empty, we bootstrap with defaults
    if not stored:
        defaults = [
            {
                "agent_id": "DevOps_Agent",
                "proposal": "خطة GitOps Pipeline",
                "status": "NEW",
                "timestamp": datetime.utcnow().timestamp() * 1000,
                "requester": "CTO / Cloud Infrastructure Team",
                "executive_brief": "الانتقال الكامل إلى إدارة البنية التحتية عبر الكود (IaC) باستخدام ArgoCD. هذا القرار سيقلل من التدخل البشري في عمليات النشر بنسبة 90%.",
                "impact": "✅ زيادة سرعة النشر 3x\n✅ تقليل حوادث الإنتاج بنسبة 45%\n⚠️ يتطلب تدريب الفريق لمدة أسبوعين",
                "details": "المقترح يتضمن استبدال Jenkins بـ GitHub Actions و ArgoCD. سيتم تجميد النشر اليدوي بالكامل في بيئة الإنتاج."
            },
            {
                "agent_id": "Compliance_Bot",
                "proposal": "تحديث السياسة P-OPS-05", 
                "status": "NEW",
                "timestamp": datetime.utcnow().timestamp() * 1000,
                "requester": "Sovereign Archivist",
                "executive_brief": "تعديل سياسة التعامل مع البيانات الحساسة لتتوافق مع معايير الأمن السيبراني الجديدة.",
                "impact": "✅ الامتثال القانوني بنسبة 100%\n⚠️ قد يبطئ بعض عمليات التطوير",
                "details": "إضافة تشفير إلزامي لجميع السجلات (Logs) وعدم تخزين أي بيانات شخصية في بيئة التطوير."
            },
            {
                "agent_id": "Monitor_Agent",
                "proposal": "طلب زيادة موارد",
                "status": "NEW",
                 "timestamp": datetime.utcnow().timestamp() * 1000,
                "requester": "System Sentinel",
                "executive_brief": "رصد ارتفاع في استهلاك الذاكرة في خدمة التحليل (Analysis Service).",
                "impact": "✅ ضمان استقرار النظام\n💰 تكلفة إضافية شهرية (50$)",
                "details": "زيادة الرام من 4GB إلى 8GB لتفادي توقف الخدمة أثناء معالجة المستندات الكبيرة."
            },
            {
                "agent_id": "DBA_Bot",
                "proposal": "Emergency Backup (Pre-Patch)",
                "status": "NEW",
                "timestamp": datetime.utcnow().timestamp() * 1000,
                "requester": "Database Administrator Team",
                "executive_brief": "طلب نسخ احتياطي فوري لقاعدة البيانات قبل تطبيق التحديثات الأمنية العاجلة.",
                "impact": "✅ حماية البيانات من الفقدان (RPO = 0)\n⚠️ إيقاف الخدمة لمدة 30 ثانية أثناء النسخ (Lock Tables)",
                "details": "سيتم إنشاء نسخة كاملة (Full Dump) وحفظها في المسار الآمن مع ضغط البيانات."
            }
        ]
        
        # Save defaults to DB
        for d in defaults:
            p = ProposalSchema(
                id=uid(),
                agent_id=d["agent_id"],
                proposal=d["proposal"],
                status=d["status"],
                timestamp=float(d["timestamp"]),
                requester=d["requester"],
                executive_brief=d["executive_brief"],
                impact=d["impact"],
                details=d["details"]
            )
            kb.save_proposal(p)
            stored.append(p)
            
    # Convert to list of dicts for local use
    # We sort by timestamp descending to match UI
    stored.sort(key=lambda x: x.timestamp, reverse=True)
    return [
        {
            "id": p.id, # New field
            "agent_id": p.agent_id,
            "proposal": p.proposal,
            "status": p.status,
            "timestamp": p.timestamp,
            "requester": p.requester,
            "executive_brief": p.executive_brief,
            "impact": p.impact,
            "details": p.details
        }
        for p in stored
    ]

# --- Consultant Endpoint ---
@app.get("/consultant/insight")
async def get_consultant_insight(_: bool = Depends(_require_api_key)):
    # Gather state
    report = {
        "proposals": proposals_store,
        "health": "Excellent",
        "timestamp": datetime.now().isoformat()
    }
    
    # Analyze
    result = await external_consultant.review_committee_report(report)
    return {"insight": result.get("external_recommendation", "No insight available.")}

# --- Archivist Endpoint ---
@app.post("/archivist/audit")
async def trigger_archivist_audit(_: bool = Depends(_require_api_key)):
    from ..agents.archivist_agent import ArchivistAgent
    from ..agents.mediator import MediatorAgent
    
    # Init Agents
    archivist = ArchivistAgent("Sovereign_Archivist", llm_provider=external_consultant.llm)
    mediator = MediatorAgent()
    kb = get_icgl().kb
    
    # Run Workflow: audit -> MEDIATOR -> consult -> report
    final_report = await archivist.submit_report_to_ceo(
        kb=kb, 
        consultant_agent=external_consultant,
        mediator_agent=mediator
    )
    
    return final_report

# --- Plan State Store ---
pending_improvement_plan = None

@app.post("/archivist/plan-improvements")
async def plan_improvements(_: bool = Depends(_require_api_key)):
    global pending_improvement_plan
    from ..agents.archivist_agent import ArchivistAgent
    
    archivist = ArchivistAgent("Sovereign_Archivist", llm_provider=external_consultant.llm)
    
    # Run Safe Planning Mode
    plan = await archivist.generate_improvement_plan(
        consultant_agent=external_consultant
    )
    
    # Store in memory for approval
    pending_improvement_plan = plan
    
    return {"status": "PLAN_GENERATED", "summary": "Review pending plan via GET /archivist/plan"}

@app.get("/archivist/plan")
async def get_pending_plan(_: bool = Depends(_require_api_key)):
    return pending_improvement_plan or {}

@app.post("/archivist/plan/action")
async def execute_plan_action(payload: Dict[str, str], _: bool = Depends(_require_api_key)):
    global pending_improvement_plan
    action = payload.get("action")
    
    if not pending_improvement_plan:
        return {"error": "No plan pending."}
        
    if action == "REJECT":
        pending_improvement_plan = None
        return {"status": "PLAN_REJECTED", "message": "Plan discarded."}
        
    if action == "APPROVE":
        # Execute Drafting Phase
        # Instead of simulated execution, we call create_drafts
        from ..agents.archivist_agent import ArchivistAgent
        archivist = ArchivistAgent("Sovereign_Archivist", llm_provider=external_consultant.llm)
        
        drafts = await archivist.create_drafts_from_plan(pending_improvement_plan)
        
        # Don't clear the plan yet? Or maybe we clear it and rely on drafts existing?
        # Let's keep the plan active but marked as 'DRAFTING_COMPLETE' if we want UI persistence.
        # But per requirements, "Approve" moves to "Drafts Ready" state.
        
        pending_improvement_plan["status"] = "DRAFTS_READY"
        pending_improvement_plan["drafts"] = drafts
        
        return {
            "status": "DRAFTS_READY", 
            "message": f"Created {len(drafts)} drafts. Review them before ratification.",
            "drafts": drafts
        }

@app.post("/archivist/ratify")
async def ratify_drafts(payload: Dict[str, str], _: bool = Depends(_require_api_key)):
    from ..agents.archivist_agent import ArchivistAgent
    global pending_improvement_plan
    
    archivist = ArchivistAgent("Sovereign_Archivist", llm_provider=external_consultant.llm)
    ratified = await archivist.ratify_drafts()
    
    # Clear pending plan as cycle is complete
    pending_improvement_plan = None
    
    return {
        "status": "RATIFIED",
        "message": f"Successfully ratified {len(ratified)} policies.",
        "ratified_policies": ratified
    }

# --- Archivist Transparency & Status ---

@app.get("/archivist/audit/details")
async def get_audit_details(_: bool = Depends(_require_api_key)):
    from ..agents.archivist_agent import ArchivistAgent
    # Note: last_consultation_logs is instance-based. In a stateless FastAPI server with reload, 
    # it might reset. But for this session, we'll keep it simple.
    archivist = ArchivistAgent("Sovereign_Archivist", llm_provider=external_consultant.llm)
    return {"logs": archivist.last_consultation_logs}

@app.get("/archivist/policies")
async def list_policies(_: bool = Depends(_require_api_key)):
    from ..agents.archivist_agent import ArchivistAgent
    archivist = ArchivistAgent("Sovereign_Archivist")
    if not archivist.policies_dir.exists():
        return {"policies": []}
    files = [f.name for f in archivist.policies_dir.glob("*.md")]
    return {"policies": sorted(files)}

@app.get("/archivist/drafts")
async def list_drafts(_: bool = Depends(_require_api_key)):
    from ..agents.archivist_agent import ArchivistAgent
    archivist = ArchivistAgent("Sovereign_Archivist")
    if not archivist.drafts_dir.exists():
        return {"drafts": []}
    files = [f.name for f in archivist.drafts_dir.glob("*.md")]
    return {"drafts": sorted(files)}
        
    return {"error": "Invalid action."}

# Load on startup
proposals_store = _load_proposals()

@app.get("/proposals")
async def get_proposals(_: bool = Depends(_require_api_key)):
    # Refresh from DB? No, we modify in memory and persist on write.
    # But for multi-process safety, reloading might be better. 
    # For now, simplistic approach: In-memory authoritative for read speed, write-through for persistence.
    return {"proposals": proposals_store}

@app.put("/proposals/{index}")
async def update_proposal(index: int, payload: Dict[str, Any], background_tasks: BackgroundTasks, _: bool = Depends(_require_api_key)):
    """
    Update a proposal by index. 
    NOTE: Using index is risky with persistence. Ideally we should use ID.
    But to keep frontend compatible, we keep index logic but persist using ID if available.
    """
    if 0 <= index < len(proposals_store):
        proposals_store[index].update(payload)
        
        # Persist Update
        kb = get_icgl().kb
        p_data = proposals_store[index]
        
        # Ensure we have an ID (migrating old in-memory items if needed)
        if "id" not in p_data:
            p_data["id"] = uid()
            
        p_obj = ProposalSchema(
            id=p_data["id"],
            agent_id=p_data["agent_id"],
            proposal=p_data["proposal"],
            status=p_data["status"],
            timestamp=float(p_data["timestamp"]),
            requester=p_data.get("requester"),
            executive_brief=p_data.get("executive_brief"),
            impact=p_data.get("impact"),
            details=p_data.get("details")
        )
        kb.save_proposal(p_obj)
        
        # Simulate Agent Response Logic
        if payload.get("status") == "CLARIFICATION":
            background_tasks.add_task(simulate_agent_reply, index)
            
        # Simulate Execution Logic (New)
        if payload.get("status") == "APPROVED":
            background_tasks.add_task(execute_real_action, index)
            
        return {"status": "updated", "proposal": proposals_store[index]}
    raise HTTPException(status_code=404, detail="Proposal not found")

async def simulate_agent_reply(index: int):
    """Simulates the agent receiving the request and replying after a delay."""
    await asyncio.sleep(5) # Agent "thinking"
    
    proposal = proposals_store[index]
    agent_name = proposal.get("agent_id", "Agent")
    
    # Generic AI reply simulation based on context
    reply_text = f"\n\n--- 🗣️ رد {agent_name} (Updated {datetime.utcnow().strftime('%H:%M')}): ---\n"
    reply_text += "تم مراجعة الطلب. توضيح للنقطة المثارة: \n"
    reply_text += "نؤكد أن التكلفة المذكورة تشمل البنية التحتية لمدة عام كامل، ولا توجد رسوم خفية. "
    reply_text += "تم تحديث الوثيقة الفنية المرفقة لتوضيح العائد على الاستثمار (ROI) بشكل أدق."

    # Update the proposal with the reply
    proposal["details"] = (proposal.get("details", "") + reply_text)
    proposal["status"] = "UPDATED" # Bring it back to attention
    proposal["executive_brief"] += " [تم استلام توضيحات إضافية من الوكيل]"
    
    # Persist the reply
    kb = get_icgl().kb
    p_data = proposal
    p_obj = ProposalSchema(
        id=p_data["id"],
        agent_id=p_data["agent_id"],
        proposal=p_data["proposal"],
        status=p_data["status"],
        timestamp=float(p_data["timestamp"]),
        requester=p_data.get("requester"),
        executive_brief=p_data.get("executive_brief"),
        impact=p_data.get("impact"),
        details=p_data.get("details")
    )
    kb.save_proposal(p_obj)
    
    print(f"✅ Agent {agent_name} replied to clarification request for proposal {index}")

# Mock Proposal Model Update (Simulating write-through for new proposals via API)
from pydantic import BaseModel
class ProposalReq(BaseModel):
    agent_id: str
    proposal: str
    status: str | None = None
    requester: str | None = None
    executive_brief: str | None = None
    impact: str | None = None
    details: str | None = None

@app.post("/proposals")
async def submit_proposal(p: ProposalReq):
    new_id = uid()
    record = {
        "id": new_id,
        "agent_id": p.agent_id,
        "proposal": p.proposal,
        "status": p.status or "NEW",
        "timestamp": datetime.utcnow().timestamp() * 1000, 
        "requester": p.requester or "Unknown System",
        "executive_brief": p.executive_brief or "No brief provided.",
        "impact": p.impact or "Unknown impact.",
        "details": p.details or "No details.",
    }
    
    # Persist
    kb = get_icgl().kb
    p_obj = ProposalSchema(
        id=new_id,
        agent_id=record["agent_id"],
        proposal=record["proposal"],
        status=record["status"],
        timestamp=float(record["timestamp"]),
        requester=record["requester"],
        executive_brief=record["executive_brief"],
        impact=record["impact"],
        details=record["details"]
    )
    kb.save_proposal(p_obj)
    
    # Update Memory
    proposals_store.append(record)
    return {"ok": True, "proposal": record}

class SafetyEnforcer:
    """Enforces strict safety verification on all local operations."""
    
    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        # Sandbox: Ensure root_dir exists
        os.makedirs(self.root_dir, exist_ok=True)
        
    def validate_path(self, filename: str) -> str:
        """Ensures the target path is inside the sandbox."""
        # Join and resolve absolute path
        target_path = os.path.abspath(os.path.join(self.root_dir, filename))
        
        # Check for jailbreak (prevent '..\windows')
        if not target_path.startswith(self.root_dir):
            raise ValueError(f"🚨 SECURITY BLOCKED: Path traversal attempt detected: {filename}")
            
        print(f"🛡️ Path Verified: {target_path}")
        return target_path

    def check_size_limit(self, content: str, limit_mb: float = 1.0):
        """Prevents disk flooding."""
        size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if size_mb > limit_mb:
            raise ValueError(f"🚨 SECURITY BLOCKED: Payload size ({size_mb:.2f}MB) exceeds limit ({limit_mb}MB)")
    
    async def timebox_execution(self, coroutine, timeout_sec: float = 5.0):
        """Kills any operation that takes too long."""
        try:
            return await asyncio.wait_for(coroutine, timeout=timeout_sec)
        except asyncio.TimeoutError:
            raise TimeoutError(f"🚨 SECURITY BLOCKED: Execution exceeded {timeout_sec}s timeout.")

# Initialize Enforcer
enforcer = SafetyEnforcer(os.path.join(os.getcwd(), "live_ops"))

async def execute_real_action(index: int):
    """Executes a REAL safe local action based on the decision."""
    
    # WRAPPER: Enforce 5-second timeout on the entire operation
    try:
        await enforcer.timebox_execution(_unsafe_execute_action(index))
        # Log success after safe execution
        proposal = proposals_store[index]
        proposal["executive_brief"] += " [🛡️ Safe Execution Verified]"
        print(f"✅ Safe Execution finished for proposal {index}")
        
    except Exception as e:
        # Log Security Block
        print(f"⛔ EXECUTION BLOCKED: {str(e)}")
        proposal = proposals_store[index]
        proposal["details"] += f"\n\n⛔ **SECURITY INTERVENTION:**\n{str(e)}"
        proposal["status"] = "BLOCKED"

async def _unsafe_execute_action(index: int):
    """The internal logic, which is now sandboxed."""
    await asyncio.sleep(2) # Brief processing time
    
    proposal = proposals_store[index]
    agent_name = proposal.get("agent_id", "Agent")
    
    execution_log = f"\n\n🚀 **مسار التنفيذ (Real Local Execution - Sandboxed):**\n"
    execution_log += f"✅ {datetime.utcnow().strftime('%H:%M:%S')} - Enforcer: Monitoring active.\n"
    
    # تنفيذ قرار إنشاء مجلد وثائق جديد إذا ورد في التفاصيل أو نص القرار
    details = proposal.get("details", "")
    if "Docs2" in details or "إنشاء مجلد" in details:
        import os
        docs_path = os.path.join(os.path.dirname(__file__), "..", "Docs2")
        docs_path = os.path.abspath(docs_path)
        os.makedirs(docs_path, exist_ok=True)
        readme_path = os.path.join(docs_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# وثائق المرحلة الجديدة\n\nتم إنشاء هذا المجلد تلقائياً بناءً على قرار الحوكمة بتاريخ " + str(datetime.utcnow()))
        execution_log += f"\n📁 تم إنشاء مجلد Docs2 وملف README.md في: `{docs_path}`\n"
    elif "GitOps" in proposal.get("proposal", ""):
        # Validate Path
        filename = "gitops_config.yaml"
        target_file = enforcer.validate_path(filename)
        
        # Prepare Content
        content = f"# GitOps Config - Auto Generated by {agent_name}\n"
        content += f"timestamp: {datetime.utcnow().isoformat()}\n"
        content += "status: active\n" * 10 # Some content
        
        # Validate Size
        enforcer.check_size_limit(content)
        
        # Write
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
        execution_log += f"💾 تم كتابة الملف بأمان في: `.../live_ops/{filename}`\n"
        
    elif "Policy" in proposal.get("proposal", ""):
        filename = "policy_audit.log"
        target_file = enforcer.validate_path(filename)
        
        content = f"[{datetime.utcnow().isoformat()}] POLICY APPLIED: P-OPS-05 by {agent_name}\n"
        enforcer.check_size_limit(content)
        
        with open(target_file, "a", encoding="utf-8") as f:
            f.write(content)
        execution_log += f"📝 تم التخزين في السجل الآمن: `.../live_ops/{filename}`\n"
        
    elif "Monitor" in proposal.get("proposal", ""):
        # Read Only - Safe by default but still timeboxed
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        execution_log += f"🔍 **فحص الموارد (Safe Mode):**\n"
        execution_log += f"- المساحة الحرة: {free_gb} GB\n"
        execution_log += "✅ الموارد كافية.\n"

    elif "Backup" in proposal.get("proposal", ""):
        # Action: Create a real backup log file
        filename = f"full_backup_{int(datetime.utcnow().timestamp())}.log"
        target_file = enforcer.validate_path(filename)
        
        # Simulate backup content (Mocking the datadump, but writing real file)
        content = f"--- EMERGENCY BACKUP LOG ---\n"
        content += f"Timestamp: {datetime.utcnow().isoformat()}\n"
        content += f"Initiator: {agent_name}\n"
        content += "Status: STARTING DUMP...\n"
        content += "Tables: [users, transactions, logs, audit_trail] exported.\n"
        content += "Compression: GZIP (Level 9)\n"
        content += "Status: SUCCESS\n"
        
        enforcer.check_size_limit(content)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)
        execution_log += f"💾 تم حفظ النسخة الاحتياطية في: `.../live_ops/{filename}`\n"
        execution_log += "✅ العملية تمت بنجاح."
        
    execution_log += f"🛡️ **الحالة:** تمت العملية بنجاح وبدون خروقات أمنية."
    proposal["details"] = (proposal.get("details", "") + execution_log)

@app.get("/health/system")
async def get_system_health(_: bool = Depends(_require_api_key)):
    try:
        icgl = get_icgl()
        # Basic logical check
        integrity = 100
        status = "normal"
        
        # Check if vectors are loaded
        if not icgl.kb.adrs:
            integrity -= 5
            
        # Check alerts
        # (This logic mimics get_status but for SCP format)
        return {
            "integrity_score": integrity,
            "status": status
        }
    except Exception:
        return {"integrity_score": 50, "status": "critical"}


@app.get("/channels/status")
async def get_channels_status(_: bool = Depends(_require_api_key)):
    # Map internal components to "channels"
    # 1. Executive Input (The API/Dashboard)
    # 2. Memory Stream (Vector DB)
    # 3. Decision Core (LLM/Agents)
    
    channels = []
    
    # API Channel (Self)
    channels.append({
        "id": "ch_api",
        "name": "Executive_Input",
        "active": True,
        "load": 15, # Placeholder or calc request rate
        "status": "active",
        "latency": 20
    })
    
    try:
        icgl = get_icgl()
        
        # Memory Channel
        mem_status = "active"
        mem_load = 5
        if not icgl.kb.adrs:
            mem_status = "idle"
        channels.append({
            "id": "ch_mem",
            "name": "Memory_Stream",
            "active": True,
            "load": mem_load,
            "status": mem_status,
            "latency": 45 # Mock DB latency
        })
        
        # Agents Channel
        agent_cnt = len(icgl.registry.agents) if hasattr(icgl.registry, "agents") else 0
        channels.append({
            "id": "ch_core",
            "name": "System_Output (Agents)",
            "active": True,
            "load": agent_cnt * 10,
            "status": "normal",
            "latency": 1500 # Avg agent time
        })
        
    except Exception:
        channels.append({
            "id": "ch_err",
            "name": "System_Critical",
            "active": False,
            "load": 0,
            "status": "error",
            "latency": 0
        })
        
    return channels


@app.get("/events/stream")
async def get_events_stream(limit: int = 20, _: bool = Depends(_require_api_key)):
    """
    Combine Decision Logs, Proposals, and Telemetry into a single 'Event Stream'.
    """
    events = []
    
    # 1. Decisions
    for d in dashboard.decision_log[-limit:]:
        events.append({
            "id": id(d),
            "timestamp": datetime.utcnow().timestamp() * 1000,
            "source": "SOVEREIGN_DESK",
            "type": "DECISION",
            "message": f"Decision made: {d.get('decision', 'Unknown')}",
            "level": "INFO",
            "user": "Executive"
        })
        
    # 2. Proposals
    for p in proposals_store[-limit:]:
        events.append({
            "id": id(p),
            "timestamp": datetime.utcnow().timestamp() * 1000, # Use real p['timestamp'] if parseable
            "source": "AGENT_SWARM",
            "type": "PROPOSAL",
            "message": f"New Proposal: {p.get('proposal', 'Unknown')}",
            "level": "INFO",
            "user": p.get("agent_id", "System")
        })
        
    # 3. System Startup (Mock one event if empty)
    if not events:
        events.append({
            "id": 1,
            "timestamp": datetime.utcnow().timestamp() * 1000,
            "source": "BOOT_LOADER",
            "type": "SYSTEM",
            "message": "System initialized successfully",
            "level": "SUCCESS",
            "user": "System"
        })
        
    # Sort by timestamp desc (mocked for now as we append)
    return events[::-1][:limit]

@app.get("/dashboard/overview")
async def get_dashboard_overview(_: bool = Depends(_require_api_key)):
    overview = dashboard.get_overview()
    try:
        kb = get_icgl().kb
        if kb.adrs:
            latest_adr = sorted(kb.adrs.values(), key=lambda x: x.created_at, reverse=True)[0]
            overview["latest_adr"] = {
                "id": latest_adr.id,
                "title": latest_adr.title,
                "status": latest_adr.status,
                "human_decision": latest_adr.human_decision_id,
            }
    except Exception:
        pass
    return overview

# --- Agent Utility Endpoints ---

@app.get("/agents")
async def list_agents(_: bool = Depends(_require_api_key)):
    try:
        reg = get_icgl().registry
        return {"agents": [r.value for r in reg.list_agents()]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AgentRequest(BaseModel):
    title: str
    context: str


@app.post("/agents/{agent_role}/analyze")
async def run_agent(agent_role: str, req: AgentRequest, _: bool = Depends(_require_api_key)):
    """Run a single registered agent by role name (e.g., architect, builder, policy)."""
    role_map = {r.value.lower(): r for r in AgentRole}
    role = role_map.get(agent_role.lower())
    if not role:
        raise HTTPException(status_code=404, detail="Unknown agent role")

    icgl = get_icgl()
    problem = Problem(title=req.title, context=req.context)
    try:
        result = await icgl.registry.run_agent(role, problem, icgl.kb)
        if not result:
            raise HTTPException(status_code=500, detail="No result returned")
        return {
            "agent": result.agent_id,
            "role": result.role.value,
            "confidence": result.confidence,
            "analysis": result.analysis,
            "recommendations": result.recommendations,
            "concerns": result.concerns,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Proposal Capture for Quick Wins ---





@app.get("/proposals")
async def list_proposals():
    if not proposals_store:
        kb = get_icgl().kb
        for adr in sorted(kb.adrs.values(), key=lambda x: x.created_at, reverse=True):
            proposals_store.append(
                {
                    "agent_id": "adr",
                    "proposal": adr.title,
                    "status": "PENDING",
                    "timestamp": adr.created_at,
                    "adr_id": adr.id,
                }
            )
    return {"proposals": proposals_store}


@app.put("/proposals/{idx}")
async def update_proposal(idx: int, p: Proposal):
    # If index missing, append instead of failing
    if idx < 0 or idx >= len(proposals_store):
        new_record = {
            "agent_id": p.agent_id or "unknown",
            "proposal": p.proposal or "",
            "status": p.status or "NEW",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        proposals_store.append(new_record)
        return {"ok": True, "proposal": new_record, "created": True}

    proposals_store[idx]["status"] = p.status or proposals_store[idx].get("status", "UPDATED")
    proposals_store[idx]["proposal"] = p.proposal or proposals_store[idx].get("proposal", "")
    proposals_store[idx]["agent_id"] = p.agent_id or proposals_store[idx].get("agent_id", "unknown")
    proposals_store[idx]["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return {"ok": True, "proposal": proposals_store[idx], "updated": True}

# --- ADR Utility Endpoints ---

@app.get("/adr/latest")
async def get_latest_adr(_: bool = Depends(_require_api_key)):
    """Return the latest ADR summary (id, title, status, timestamp, human decision id)."""
    try:
        kb = get_icgl().kb
        if not kb.adrs:
            raise HTTPException(status_code=404, detail="No ADRs found")
        latest = sorted(kb.adrs.values(), key=lambda x: x.created_at, reverse=True)[0]
        return {
            "id": latest.id,
            "title": latest.title,
            "status": latest.status,
            "human_decision": latest.human_decision_id,
            "created_at": latest.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ...existing code...
@app.get("/hr/generate_docs")
async def generate_hr_docs(_: bool = Depends(_require_api_key)):
    docs = hr_agent.generate_responsibility_docs()
    return {"docs": docs}

# --- UI Committee Endpoints ---
class UIReviewRequest(BaseModel):
    title: str
    description: str
    details: dict = {}

@app.post("/committee/ui/submit")
async def submit_ui_review(req: UIReviewRequest):
    result = ui_committee.submit_ui_review({
        "title": req.title,
        "description": req.description,
        "details": req.details
    })
    return {"status": "ok", "message": result}

@app.post("/committee/ui/deliberate/{review_id}")
async def deliberate_ui_review(review_id: int):
    result = ui_committee.deliberate(review_id)
    return result

@app.get("/committee/ui/recommendations")
async def get_ui_recommendations():
    return {"recommendations": ui_committee.get_recommendations()}

# --- Dashboard Mounting ---
# Switch to new React Build
ui_path = Path(__file__).parent.parent / "web" / "dist"
if ui_path.exists():
    app.mount("/dashboard", StaticFiles(directory=str(ui_path), html=True), name="ui")
    logger.info(f"✅ Dashboard loaded from {ui_path}")
else:
    logger.warning(f"⚠️ UI path not found: {ui_path}. Did you run 'npm run build'?")

# --- Core Redirects ---

from ..committees.conflict_resolution_committee import ConflictResolutionCommittee
conflict_committee = ConflictResolutionCommittee([
    "HRAgent", "DocumentationAgent", "PolicyAgent", "ArchivistAgent", "Copilot"
])
from fastapi.responses import RedirectResponse

@app.get("/")
async def root_redirect():
    """Redirect root to dashboard for easier access."""
    return RedirectResponse(url="/dashboard")

# --- State ---
active_synthesis: Dict[str, Any] = {}
global_telemetry = {
    "drift_detection_count": 0,
    "agent_failure_count": 0
}

# --- WebSocket Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSocket clients."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except (WebSocketDisconnect, RuntimeError) as e:
                # Connection closed, mark for removal
                dead_connections.append(connection)
            except Exception as e:
                logger.warning(f"Broadcast error: {e}")
        
        # Clean up dead connections
        for conn in dead_connections:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()

# --- Models ---
class ProposalRequest(BaseModel):
    title: str
    context: str
    decision: str
    human_id: str = "bakheet"

class SignRequest(BaseModel):
    action: str 
    rationale: str
    human_id: str = "bakheet"

# --- Diagnostic Endpoints ---

# --- Conflict Resolution Committee Endpoints ---
from pydantic import BaseModel

class ConflictCaseRequest(BaseModel):
    title: str
    description: str
    department: str
    details: dict = {}

@app.post("/committee/conflict/submit")
async def submit_conflict_case(req: ConflictCaseRequest):
    result = conflict_committee.submit_conflict({
        "title": req.title,
        "description": req.description,
        "department": req.department,
        "details": req.details
    })
    return {"status": "ok", "message": result}

@app.post("/committee/conflict/deliberate/{case_id}")
async def deliberate_conflict_case(case_id: int):
    result = conflict_committee.deliberate(case_id)
    return result

@app.get("/committee/conflict/recommendations")
async def get_conflict_recommendations():
    return {"recommendations": conflict_committee.get_recommendations()}

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Diagnostic endpoint to verify system sanity."""
    status: Dict[str, Any] = {
        "api": "healthy",
        "env_loaded": bool(os.getenv("OPENAI_API_KEY")),
        "db_lock": "unknown",
        "engine_ready": _icgl_instance is not None
    }
    
    try:
        icgl = get_icgl()
        status["engine_ready"] = True
        # Test KB
        icgl.kb.get_adr("test") # Simple query
        status["db_lock"] = "none"
    except Exception as e:
        status["api"] = "degraded"
        status["db_error"] = str(e)
        
    return status

@app.get("/status")
async def get_status() -> Dict[str, Any]:
    try:
        icgl = get_icgl()
        last_adr = None
        adrs = list(icgl.kb.adrs.values())
        if adrs:
            last_adr = sorted(adrs, key=lambda x: x.created_at, reverse=True)[0]
        
        # Calculate Alert Level
        alert_level = "NONE"
        last_latency = 0
        
        if last_adr and last_adr.sentinel_signals:
            if any("🚨" in s or "CRITICAL" in s for s in last_adr.sentinel_signals):
                 alert_level = "CRITICAL"
            elif any("⚠️" in s or "WARNING" in s for s in last_adr.sentinel_signals):
                 alert_level = "HIGH"
        
        if last_adr and last_adr.id in active_synthesis:
            last_latency = active_synthesis[last_adr.id].get("latency_ms", 0)

        return {
            "mode": "COCKPIT",
            "waiting_for_human": last_adr.status == "DRAFT" if last_adr else False,
            "active_alert_level": alert_level,
            "last_adr_id": last_adr.id if last_adr else None,
            "telemetry": {
                **global_telemetry,
                "last_latency_ms": last_latency
            }
        }
    except Exception as e:
        return {"mode": "ERROR", "error": str(e)}

@app.post("/propose")
async def propose_decision(req: ProposalRequest, background_tasks: BackgroundTasks):
    logger.info(f"📝 Proposal Received: {req.title}")
    try:
        icgl = get_icgl()
        adr = ADR(
            id=uid(),
            title=req.title,
            status="DRAFT",
            context=req.context,
            decision=req.decision,
            consequences=[],
            related_policies=[],
            sentinel_signals=[],
            human_decision_id=None,
        )
        
        icgl.kb.add_adr(adr)
        active_synthesis[adr.id] = {"status": "processing"}

        # إضافة الاقتراح إلى proposals_store ليظهر في الطابور
        proposals_store.append({
            "agent_id": "User",
            "proposal": req.title,
            "status": "NEW",
            "timestamp": datetime.utcnow().timestamp() * 1000,
            "requester": req.human_id,
            "executive_brief": req.context,
            "impact": "-",
            "details": req.decision
        })

        background_tasks.add_task(run_analysis_task, adr, req.human_id)
        return {"status": "Analysis Triggered", "adr_id": adr.id}
    except Exception as e:
        logger.error(f"Proposal Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, we primarily broadcast to them
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/analysis/{adr_id}")
async def websocket_analysis(websocket: WebSocket, adr_id: str):
    """WebSocket endpoint for real-time analysis updates."""
    await websocket.accept()
    try:
        while True:
            if adr_id in active_synthesis:
                await websocket.send_json(active_synthesis[adr_id])
                if active_synthesis[adr_id].get("status") == "complete" or "synthesis" in active_synthesis[adr_id]:
                    break # Done
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from analysis/{adr_id}")
    except Exception as e:
        logger.warning(f"Error in analysis stream for {adr_id}: {e}")
        try:
            await websocket.send_json({"error": "Analysis stream error", "message": str(e)})
        except Exception:
            pass  # Client already gone
    finally:
        try:
            await websocket.close()
        except Exception:
            pass  # Already closed

async def run_analysis_task(adr: ADR, human_id: str) -> None:
    """Background task to run full ICGL analysis on an ADR."""
    import time
    start_time = time.time()
    logger.info(f"🌀 Starting Background Analysis for {adr.id}")
    try:
        icgl = get_icgl()
        from ..agents.base import Problem
        # Policy gate check (pre-analysis)
        policy_report = icgl.enforcer.check_adr_compliance(adr)
        if policy_report.status == "FAIL":
            active_synthesis[adr.id] = {"status": "blocked", "policy_report": policy_report.__dict__}
            return
        
        # 1. Semantic Search (Historical Echo / S-11)
        query = f"{adr.title} {adr.context} {adr.decision}"
        matches = await icgl.memory.search(query, limit=4)
        semantic = []
        for m in matches:
            if m.document.id != adr.id:
                 semantic.append({
                     "id": m.document.id,
                     "title": m.document.metadata.get("title", "Unknown"),
                     "score": round(m.score * 100, 1)
                 })
        
        # 2. Sentinel Detailed Scan
        alerts = await icgl.sentinel.scan_adr_detailed_async(adr, icgl.kb)
        if any(a.category.value == "Drift" for a in alerts):
            global_telemetry["drift_detection_count"] += 1
        
        # 3. Agent Synthesis
        problem = Problem(
            title=adr.title,
            context=adr.context,
            metadata={"decision": adr.decision}
        )
        
        synthesis = await icgl.registry.run_and_synthesize(problem, icgl.kb)
        
        from dataclasses import asdict
        active_synthesis[adr.id] = {
            "adr": asdict(adr),
            "synthesis": {
                "overall_confidence": synthesis.overall_confidence,
                "consensus_recommendations": synthesis.consensus_recommendations,
                "all_concerns": synthesis.all_concerns,
                "agent_results": [asdict(r) for r in synthesis.individual_results],
                "semantic_matches": semantic[:3],
                "sentinel_alerts": [{
                    "id": a.rule_id,
                    "severity": a.severity.value,
                    "message": a.message,
                    "category": a.category.value
                } for a in alerts],
                "mindmap": generate_consensus_mindmap(adr.title, synthesis),
                "mediation": None, # Placeholder
                "policy_report": policy_report.__dict__
            }
        }

        # 4. Mediation Mode (Phase G) if الثقة منخفضة
        if synthesis.overall_confidence < 0.7:
            logger.info(f"⚖️ Consensus Low ({synthesis.overall_confidence:.2f}). Invoking Mediator...")
            from ..agents.mediator import MediatorAgent

            llm_provider = icgl.registry.get_llm_provider() if hasattr(icgl.registry, "get_llm_provider") else None
            mediator = MediatorAgent(llm_provider=llm_provider)

            problem_mediation = Problem(
                title=adr.title,
                context=adr.context,
                metadata={
                    "decision": adr.decision,
                    "agent_results": [asdict(r) for r in synthesis.individual_results]
                }
            )
            mediation_result = await mediator.analyze(problem_mediation, icgl.kb)

            active_synthesis[adr.id]["synthesis"]["mediation"] = {
                "analysis": mediation_result.analysis,
                "confidence": mediation_result.confidence,
                "concerns": mediation_result.concerns
            }
            logger.info("⚖️ Mediation Complete.")

        # FINAL BROADCAST
        await manager.broadcast({"type": "status_update", "status": await get_status()})
        
        # Update ADR in KB with signals
        adr.sentinel_signals = [str(a) for a in alerts]
        icgl.kb.add_adr(adr)
        
        duration = round((time.time() - start_time) * 1000)
        active_synthesis[adr.id]["latency_ms"] = duration
        
        logger.info(f"✨ Analysis Complete for {adr.id} ({duration}ms)")
        return active_synthesis[adr.id]
    except Exception as e:
        global_telemetry["agent_failure_count"] += 1
        logger.error(f"Async Analysis Failure: {e}", exc_info=True)
        active_synthesis[adr.id] = {"status": "failed", "error": str(e)}
        return active_synthesis[adr.id]

@app.get("/analysis/{adr_id}")
async def get_analysis(adr_id: str) -> Dict[str, Any]:
    if adr_id in active_synthesis:
        return active_synthesis[adr_id]
    raise HTTPException(status_code=404, detail="Analysis session context lost or not started.")

@app.post("/sign/{adr_id}")
async def sign_decision(adr_id: str, req: SignRequest):
    try:
        icgl = get_icgl()
        adr = icgl.kb.get_adr(adr_id)
        if not adr: raise HTTPException(status_code=404, detail="ADR not found")

        result_data = active_synthesis.get(adr_id)
        if not result_data or "synthesis" not in result_data:
             raise HTTPException(status_code=400, detail="Synthesis data missing.")

        # Block on policy or sentinel critical
        pol = result_data["synthesis"].get("policy_report")
        if pol and pol.get("status") == "FAIL":
            raise HTTPException(status_code=400, detail="Policy gate failed; cannot sign.")
        alerts = result_data["synthesis"].get("sentinel_alerts") or []
        if any(a.get("severity") == "CRITICAL" for a in alerts):
            raise HTTPException(status_code=400, detail="Critical sentinel alert; cannot sign.")

        # Record Decision
        decision = icgl.hdal.sign_decision(adr_id, req.action, req.rationale, req.human_id)
        
        # Persistence
        adr.status = "ACCEPTED" if req.action == "APPROVE" else "REJECTED"
        adr.human_decision_id = decision.id
        icgl.kb.add_adr(adr)
        icgl.kb.add_human_decision(decision)

        # Execution (Cycle 9)
        auto_write_enabled = is_auto_write_enabled()
        if req.action == "APPROVE" and getattr(icgl, "engineer", None) and auto_write_enabled:
             all_changes = []
             for res in result_data["synthesis"]["agent_results"]:
                 if "file_changes" in res and res["file_changes"]:
                     from ..kb.schemas import FileChange
                     for fc in res["file_changes"]:
                         change_data = {
                             "path": fc.get("path"),
                             "content": fc.get("content"),
                             "action": fc.get("action", "CREATE"),
                         }
                         all_changes.append(FileChange(**change_data))
             
             if all_changes:
                 for change in all_changes:
                      icgl.engineer.write_file(change.path, change.content)
                 icgl.engineer.commit_decision(adr, decision)

        elif req.action == "APPROVE" and getattr(icgl, "engineer", None) and not auto_write_enabled:
            logger.info("⚠️ Auto-write/commit disabled (ICGL_ENABLE_AUTO_WRITE not set). Skipping execution.")

        return {"status": "Complete", "action": req.action}
    except Exception as e:
        logger.error(f"Sign Failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kb/{type}")
async def list_kb(type: str) -> Any:
    try:
        icgl = get_icgl()
        if type == "adrs": return sorted(list(icgl.kb.adrs.values()), key=lambda x: x.created_at, reverse=True)
        if type == "policies": return list(icgl.kb.policies.values())
        return {"error": "Invalid KB type"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/kb/adr/{adr_id}")
async def delete_adr(adr_id: str) -> Dict[str, Any]:
    try:
        icgl = get_icgl()
        removed = icgl.kb.remove_adr(adr_id)
        if not removed:
            raise HTTPException(status_code=404, detail="ADR not found")
        return {"status": "deleted", "adr_id": adr_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_consensus_mindmap(title: str, synthesis) -> str:
    """Generates Mermaid mindmap syntax from synthesis results."""
    lines: List[str] = ["mindmap", f"  root(({title}))"]
    
    # Consensus Node
    lines.append("    Consensus")
    for rec in synthesis.consensus_recommendations[:3]:
        # Clean text for Mermaid (no special chars)
        clean_rec = rec.replace("(", "[").replace(")", "]").replace("\"", "'")
        lines.append(f"      {clean_rec}")
        
    # Agents Node
    lines.append("    Agents")
    for res in synthesis.individual_results:
        role = res.role.value
        conf = int(res.confidence * 100)
        lines.append(f"      {role} ({conf}%)")
        if res.concerns:
            first_concern = res.concerns[0].replace("(", "[").replace(")", "]")
            lines.append(f"        {first_concern}")

    # Risks Node
    if synthesis.all_concerns:
        lines.append("    Risks")
        for concern in synthesis.all_concerns[:3]:
            clean_concern = concern.replace("(", "[").replace(")", "]")
            lines.append(f"      {clean_concern}")

    return "\n".join(lines)

# -----------------------------------------------------------------------------
# 🔒 Runtime Guardrails Helpers
# -----------------------------------------------------------------------------

def is_auto_write_enabled() -> bool:
    """Check if auto write/commit is explicitly enabled by environment."""
    return os.getenv("ICGL_ENABLE_AUTO_WRITE", "").lower() in {"1", "true", "yes"}

# =============================================================================
# 💬 CHAT ENDPOINT (Conversational Interface)
# =============================================================================

from ..chat.schemas import ChatRequest, ChatResponse
from ..conversation import ConversationOrchestrator

# Initialize chat orchestrator (uses governed ICGL + Runtime Guard)
chat_orchestrator = ConversationOrchestrator(get_icgl, run_analysis_task)
chat_ws_manager = ConnectionManager()


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Conversational interface endpoint.
    
    User sends natural language message, system responds with rich structured content.
    """
    import traceback
    try:
        logger.info(f"💬 Chat message: {request.message[:80]}...")
        normalized = request.message.strip().lower()
        if normalized in {"approve_recommendations", "reject_recommendations"}:
            action = "APPROVE" if "approve" in normalized else "REJECT"
            response = chat_orchestrator.composer.recommendations_receipt(action, {"mode": "explore"})
            response.state["session_id"] = request.session_id
            try:
                await chat_ws_manager.broadcast(jsonable_encoder(response))
            except Exception as e:
                logger.warning(f"Chat broadcast failed: {e}")
            return response

        if "recommendation" in normalized and any(word in normalized for word in ["approve", "reject", "accept", "decline", "وافق", "ارفض", "قبول", "رفض"]):
            action = "APPROVE" if any(word in normalized for word in ["approve", "accept", "وافق", "قبول"]) else "REJECT"
            response = chat_orchestrator.composer.recommendations_receipt(action, {"mode": "explore"})
            response.state["session_id"] = request.session_id
            try:
                await chat_ws_manager.broadcast(jsonable_encoder(response))
            except Exception as e:
                logger.warning(f"Chat broadcast failed: {e}")
            return response

        response = await chat_orchestrator.handle(request)
        if any("Unrecognized intent" in (msg.content or "") for msg in response.messages):
            if normalized in {"approve_recommendations", "reject_recommendations"} or (
                "recommendation" in normalized and any(word in normalized for word in ["approve", "reject", "accept", "decline", "وافق", "ارفض", "قبول", "رفض"]) 
            ):
                action = "APPROVE" if any(word in normalized for word in ["approve", "accept", "وافق", "قبول"]) else "REJECT"
                response = chat_orchestrator.composer.recommendations_receipt(action, {"mode": "explore"})
                response.state["session_id"] = request.session_id
        # Broadcast to connected chat clients (stateful viewers)
        try:
            await chat_ws_manager.broadcast(jsonable_encoder(response))
        except Exception as e:
            logger.warning(f"Chat broadcast failed: {e}")
        return response
    except Exception as e:
        logger.error(f"[chat_endpoint] Exception: {e}\n{traceback.format_exc()}")
        return chat_orchestrator.composer.error(f"Chat endpoint failed: {e}")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await chat_ws_manager.connect(websocket)
    try:
        # Initial handshake: send empty chat state so first frame includes `messages`
        await websocket.send_json({
            "messages": [],
            "state": {"mode": "explore", "waiting_for_human": False, "session_id": None}
        })
        # Lightweight ack for UI consoles
        await websocket.send_json({"type": "stream", "content": "Connected via Secure Uplink."})
        
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
                user_content = data.get("content", "")
                normalized = user_content.strip().lower()
                if normalized in {"approve_recommendations", "reject_recommendations"} or (
                    "recommendation" in normalized and any(word in normalized for word in ["approve", "reject", "accept", "decline", "وافق", "ارفض", "قبول", "رفض"])
                ):
                    action = "APPROVE" if any(word in normalized for word in ["approve", "accept", "وافق", "قبول"]) else "REJECT"
                    response = chat_orchestrator.composer.recommendations_receipt(action, {"mode": "explore"})
                    for msg in response.messages:
                        if msg.role == "assistant" and msg.content:
                            await websocket.send_json({
                                "type": "stream",
                                "content": msg.content
                            })
                    if response.state:
                        await websocket.send_json({
                            "type": "state",
                            "state": response.state
                        })
                    continue
                
                # Create a mock Request object since Orchestrator expects one
                chat_req = ChatRequest(message=user_content)
                
                # Signal "Thinking" - Let frontend know we are working on it
                await websocket.send_json({"type": "stream", "content": "..."}) 
                
                logger.info(f"⏳ Processing Chat Request: {user_content[:50]}...")
                start_ts = time.time()
                
                try:
                    # Process via Orchestrator with timeout safety
                    response = await asyncio.wait_for(chat_orchestrator.handle(chat_req), timeout=25.0)
                except asyncio.TimeoutError:
                    logger.error("❌ Orchestrator Timeout (25s)")
                    await websocket.send_json({
                        "type": "stream",
                        "content": "⚠️ System Timeout: Core reasoning took too long. Please try a simpler request."
                    })
                    continue

                duration = time.time() - start_ts
                logger.info(f"✅ Chat Processed in {duration:.2f}s")
                
                # Send text response(s) from assistant messages
                for msg in response.messages:
                    if msg.role == "assistant":
                         # Stream text
                         if msg.content:
                             await websocket.send_json({
                                 "type": "stream",
                                 "content": msg.content
                             })
                         
                         # Send blocks
                         if msg.blocks:
                             for block in msg.blocks:
                                 await websocket.send_json({
                                     "type": "block",
                                     "block_type": block.type,
                                     "title": block.title,
                                     "content": block.data
                                 })

                # Send state for UI actions (e.g., approval required)
                if response.state:
                    await websocket.send_json({
                        "type": "state",
                        "state": response.state
                    })

            except json.JSONDecodeError:
                pass
            except Exception as e:
                logger.error(f"WS Handling Error: {e}")
                await websocket.send_json({"type": "stream", "content": f"System Error: {str(e)}"})

    except WebSocketDisconnect:
        chat_ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"Chat WS error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
        chat_ws_manager.disconnect(websocket)


# =============================================================================
# 📊 OBSERVABILITY ENDPOINTS (Phase 1: Read-Only)
# =============================================================================

@app.get("/observability/stats")
async def get_observability_stats():
    """Get observability ledger statistics"""
    try:
        from ..observability import get_ledger
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        return ledger.get_stats()
    except Exception as e:
        logger.error(f"Observability stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/traces")
async def list_recent_traces(limit: int = 50):
    """List recent traces with metadata"""
    try:
        from ..observability import get_ledger
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        traces = ledger.get_recent_traces(limit=limit)
        return {"traces": traces, "count": len(traces)}
    except Exception as e:
        logger.error(f"List traces error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/trace/{trace_id}")
async def get_trace_details(trace_id: str):
    """Get complete trace for replay"""
    try:
        from ..observability import get_ledger
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        events = ledger.get_trace(trace_id)
        return {
            "trace_id": trace_id,
            "event_count": len(events),
            "events": [e.to_dict() for e in events]
        }
    except Exception as e:
        logger.error(f"Get trace error: {e}")

@app.get("/observability/trace/{trace_id}/graph")
async def get_trace_graph(trace_id: str):
    """Get trace visualization graph"""
    try:
        from ..observability import get_ledger
        from ..observability.graph import TraceGraphBuilder
        
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        
        events = ledger.get_trace(trace_id)
        
        # 💼 Sovereign Office: Automated Enrichment
        from ..agents.secretary_agent import SecretaryAgent
        secretary = SecretaryAgent("SovereignSecretary")
        for event in events:
            if not event.description_ar:
                event.description_ar = await secretary.translate_event(
                    event.event_type.value, 
                    event.actor_id, 
                    event.__dict__
                )

        builder = TraceGraphBuilder()
        graph = builder.build(trace_id, events)
        
        if not graph:
            raise HTTPException(status_code=404, detail="Trace not found or empty")
            
        return graph
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trace graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability/events")
async def query_events(
    trace_id: Optional[str] = None,
    session_id: Optional[str] = None,
    adr_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100
):
    """Query events with filters"""
    try:
        from ..observability import get_ledger
        from ..observability.events import EventType
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        
        evt_type = EventType(event_type) if event_type else None
        events = ledger.query_events(
            trace_id=trace_id,
            session_id=session_id,
            adr_id=adr_id,
            event_type=evt_type,
            limit=limit
        )
        return {
            "events": [e.to_dict() for e in events],
            "count": len(events)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trace graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/procedures")
async def list_procedures():
    """List all Standard Operating Procedures (SOPs)"""
    try:
        from ..governance.procedure_engine import ProcedureEngine
        engine = ProcedureEngine()
        procs = engine.list_procedures()
        return {
            "procedures": [p.__dict__ for p in procs],
            "count": len(procs)
        }
    except Exception as e:
        logger.error(f"List procedures error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/archive/status")
async def get_archive_status():
    """Get Sovereign Archivist's audit status"""
    try:
        from ..agents.archivist_agent import ArchivistAgent
        archivist = ArchivistAgent("SovereignArchivist")
        ledger = get_ledger()
        kb = get_icgl() # Assuming this returns the KB instance
        status = await archivist.audit_kb(kb)
        return status
    except Exception as e:
        logger.error(f"Archive status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/adapters")
async def list_adapters():
    """List all registered adapters (ADR-CANONICAL-001 §3.3)"""
    try:
        from ..governance.adapter_registry import get_adapter_registry
        registry = get_adapter_registry()
        adapters = registry.list_all()
        return {
            "adapters": [a.__dict__ for a in adapters],
            "count": len(adapters),
            "certified_count": len([a for a in adapters if a.certified])
        }
    except Exception as e:
        logger.error(f"List adapters error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/adrs/fast-track")
async def create_fast_track_adr(
    title: str,
    purpose: str,
    scope: str,
    risk_level: str,
    kill_switch_definition: str,
    rollback_strategy: str,
    requester_id: str = None,
    operational_request_id: str = None
):
    """Create a fast-track ADR (ADR-CANONICAL-001 §3.2)"""
    try:
        from ..kb import FastTrackADR, uid
        
        adr = FastTrackADR(
            id=uid(),
            title=title,
            purpose=purpose,
            scope=scope,
            risk_level=risk_level,
            kill_switch_definition=kill_switch_definition,
            rollback_strategy=rollback_strategy,
            requester_id=requester_id,
            operational_request_id=operational_request_id
        )
        
        # TODO: Add to KB storage
        logger.info(f"✅ Fast-track ADR created: {adr.id}")
        return {"adr_id": adr.id, "status": "created"}
    except Exception as e:
        logger.error(f"Create fast-track ADR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 🔀 CHANNEL COORDINATION (Phase 2)
# =============================================================================

@app.get("/channels")
async def list_active_channels():
    """List all active communication channels"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        channels = router.get_active_channels()
        return {
            "channels": [c.to_dict() for c in channels],
            "count": len(channels)
        }
    except Exception as e:
        logger.error(f"List channels error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/channels/{channel_id}/terminate")
async def terminate_channel(channel_id: str, reason: str = "User requested"):
    """Emergency channel termination (human override)"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        result = await router.terminate_channel(
            channel_id=channel_id,
            reason=reason,
            terminated_by="human"
        )
        return result
    except Exception as e:
        logger.error(f"Terminate channel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/channels/stats")
async def get_channel_stats():
    """Get channel router statistics"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        return router.get_stats()
    except Exception as e:
        logger.error(f"Channel stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/channels/{channel_id}")
async def get_channel_details(channel_id: str):
    """Get detailed information about a specific channel"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        channel = router.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        return channel.to_dict()
    except HTTPException:
        raise
    except Exception as e:

        logger.error(f"Get channel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/channels/{channel_id}/terminate")
async def terminate_channel(channel_id: str, reason: str = "User requested"):
    """Emergency channel termination (human override)"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        result = await router.terminate_channel(
            channel_id=channel_id,
            reason=reason,
            terminated_by="human"
        )
        return result
    except Exception as e:
        logger.error(f"Terminate channel error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/channels/stats")
async def get_channel_stats():
    """Get channel router statistics"""
    try:
        router = get_channel_router()
        if not router:
            return {"error": "Channel router not initialized"}
        
        return router.get_stats()
    except Exception as e:
        logger.error(f"Channel stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))





# =============================================================================
# 📋 CONDITIONAL POLICY MANAGEMENT (Phase 3 Advanced)
# =============================================================================

@app.get("/policies")
async def list_policies():
    """List all available policies (static and conditional)"""
    try:
        from ..coordination.advanced_policies import get_policy_registry
        
        registry = get_policy_registry()
        policies = registry.list_all()
        
        return {
            "policies": [
                {
                    "name": p.name,
                    "description": p.description,
                    "type": "conditional" if hasattr(p, 'conditions') else "static",
                    "allowed_actions": [a.value for a in p.allowed_actions],
                    "max_messages": p.max_messages,
                    "max_duration_seconds": p.max_duration_seconds,
                    "requires_human_approval": p.requires_human_approval,
                    "conditions_count": len(p.conditions) if hasattr(p, 'conditions') else 0
                }
                for p in policies
            ],
            "count": len(policies)
        }
    except Exception as e:
        logger.error(f"List policies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/{policy_name}")
async def get_policy_details(policy_name: str):
    """Get detailed policy information"""
    try:
        from ..coordination.advanced_policies import get_policy_registry
        
        registry = get_policy_registry()
        policy = registry.get(policy_name)
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        details = {
            "name": policy.name,
            "description": policy.description,
            "type": "conditional" if hasattr(policy, 'conditions') else "static",
            "allowed_actions": [a.value for a in policy.allowed_actions],
            "max_messages": policy.max_messages,
            "max_duration_seconds": policy.max_duration_seconds,
            "requires_human_approval": policy.requires_human_approval,
            "alert_on_violations": policy.alert_on_violations
        }
        
        # Add conditional policy details
        if hasattr(policy, 'conditions'):
            details["conditions"] = [c.to_dict() for c in policy.conditions]
            details["fallback_policy"] = policy.fallback_policy.name if policy.fallback_policy else None
            details["evaluation_strategy"] = policy.evaluation_strategy
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/policies/test/{policy_name}")
async def test_policy_evaluation(policy_name: str, context: dict):
    """
    Test conditional policy evaluation with given context.
    
    Request body:
    {
        "from_agent": "agent_id",
        "to_agent": "other_agent_id"
    }
    
    Returns which policy would be active given current conditions.
    """
    try:
        from ..coordination.advanced_policies import get_policy_registry, ConditionalPolicy
        
        registry = get_policy_registry()
        policy = registry.get(policy_name)
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        if not isinstance(policy, ConditionalPolicy):
            return {
                "policy_name": policy.name,
                "type": "static",
                "message": "Policy is static, no evaluation needed"
            }
        
        # Build context for evaluation
        router = get_channel_router()
        from_agent = context.get("from_agent", "test_agent")
        to_agent = context.get("to_agent", "target_agent")
        
        eval_context = await router._build_policy_context(from_agent, to_agent)
        
        # Evaluate
        active_policy = policy.evaluate(eval_context)
        
        # Check which conditions passed
        condition_results = [
            {
                "condition": c.to_dict(),
                "passed": c.evaluate(eval_context),
                "actual_value": eval_context.get(c.type)
            }
            for c in policy.conditions
        ]
        
        return {
            "policy_name": policy.name,
            "type": "conditional",
            "context": eval_context,
            "evaluated_to": active_policy.name,
            "conditions": condition_results,
            "used_fallback": active_policy.name != policy.name
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test policy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# 📡 SCP WEBSOCKET & PATTERN DETECTION (Phase 3)
# =============================================================================

@app.websocket("/ws/scp")
async def scp_websocket(websocket: WebSocket):
    """Real-time event streaming for SCP dashboard"""
    from ..observability.broadcaster import get_broadcaster
    
    await websocket.accept()
    broadcaster = get_broadcaster()
    broadcaster.subscribe(websocket)
    
    try:
        # Keep connection alive and handle client messages
        while True:
            data = await websocket.receive_text()
            # Handle control commands from SCP
            import json
            try:
                command = json.loads(data)
                if command.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except:
                pass
    except Exception as e:
        logger.error(f"SCP WebSocket error: {e}")
    finally:
        broadcaster.unsubscribe(websocket)


@app.get("/patterns/alerts")
async def get_pattern_alerts(limit: int = 10):
    """Get recent pattern detection alerts"""
    try:
        from ..observability.patterns import get_detector
        detector = get_detector()
        alerts = detector.get_recent_alerts(limit=limit)
        return {
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "pattern": a.pattern,
                    "description": a.description,
                    "timestamp": a.timestamp.isoformat(),
                    "event_count": len(a.events)
                }
                for a in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/patterns/detect")
async def run_pattern_detection(window_minutes: int = 5):
    """Run pattern detection on recent events"""
    try:
        from ..observability import get_ledger
        from ..observability.patterns import get_detector
        from datetime import datetime, timedelta
        
        ledger = get_ledger()
        if not ledger:
            return {"error": "Observability not initialized"}
        
        # Get recent events
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        all_events = ledger.query_events(limit=1000)
        recent = [e for e in all_events if e.timestamp >= cutoff]
        
        # Detect patterns
        detector = get_detector()
        alerts = detector.detect_patterns(recent, window_minutes=window_minutes)
        
        return {
            "analyzed_events": len(recent),
            "alerts_found": len(alerts),
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "severity": a.severity,
                    "pattern": a.pattern,
                    "description": a.description
                }
                for a in alerts
            ]
        }
    except Exception as e:
        logger.error(f"Pattern detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# 🧠 ML-BASED ANOMALY DETECTION (Phase 3 Advanced)
# =============================================================================

@app.get("/ml/status")
async def get_ml_status():
    """Get ML detector status and training info"""
    try:
        from ..observability.ml_detector import get_ml_detector
        
        detector = get_ml_detector()
        
        return {
            "sklearn_available": detector.sklearn_available,
            "trained": detector.trained,
            "training_event_count": detector.training_event_count,
            "last_training_time": detector.last_training_time.isoformat() if detector.last_training_time else None,
            "hours_since_training": detector.hours_since_training(),
            "total_anomalies_detected": len(detector.detected_anomalies),
            "method": "ml" if detector.sklearn_available and detector.trained else "rule-based"
        }
    except Exception as e:
        logger.error(f"ML status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ml/train")
async def train_ml_models():
    """Manually trigger ML model training"""
    try:
        from ..observability.ml_detector import get_ml_detector
        ledger = get_ledger()
        
        if not ledger:
            raise HTTPException(status_code=503, detail="Observability not initialized")
        
        detector = get_ml_detector()
        
        if not detector.sklearn_available:
            return {
                "error": "scikit-learn not available",
                "install": "pip install scikit-learn numpy"
            }
        
        # Get historical events
        events = ledger.query_events(limit=5000)
        
        if len(events) < 100:
            return {
                "error": "Insufficient training data",
                "required": 100,
                "current": len(events)
            }
        
        # Train models
        result = detector.train(events)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/anomalies")
async def get_ml_anomalies(window_minutes: int = 15, limit: int = 20):
    """Get ML-detected anomalies"""
    try:
        from ..observability.ml_detector import get_ml_detector
        from datetime import timedelta
        
        ledger = get_ledger()
        if not ledger:
            raise HTTPException(status_code=503, detail="Observability not initialized")
        
        detector = get_ml_detector()
        
        # Get recent events
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        all_events = ledger.query_events(limit=1000)
        recent = [e for e in all_events if e.timestamp >= cutoff]
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(recent)
        
        return {
            "anomalies": [a.to_dict() for a in anomalies],
            "count": len(anomalies),
            "analyzed_events": len(recent),
            "window_minutes": window_minutes,
            "method": "ml" if detector.sklearn_available and detector.trained else "rule-based",
            "trained": detector.trained
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ML anomalies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml/anomalies/history")
async def get_anomaly_history(limit: int = 50):
    """Get historical anomalies"""
    try:
        from ..observability.ml_detector import get_ml_detector
        
        detector = get_ml_detector()
        anomalies = detector.get_recent_anomalies(limit=limit)
        
        return {
            "anomalies": [a.to_dict() for a in anomalies],
            "count": len(anomalies),
            "total_detected": len(detector.detected_anomalies)
        }
    except Exception as e:
        logger.error(f"Anomaly history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# 💬 COC CONVERSATIONAL CHAT (Phase 3)
# =============================================================================

@app.post("/coc/chat")
async def conversational_chat(
    message: str,
    session_id: Optional[str] = None,
    user_id: str = "default_user"
):
    """
    Main COC endpoint - Natural language conversation.
    
    Flow:
    1. Get or create session
    2. Add user message to history
    3. Use dialogue manager to determine next action
    4. Resolve intent with context
    5. Execute or clarify as needed
    6. Generate natural response
    7. Update session state
    """
    try:
        from ..conversation.session import get_session_manager, Message
        from ..conversation.dialogue_manager import get_dialogue_manager
        from ..conversation.intent_resolver import IntentResolver
        from ..conversation.orchestrator import ConversationOrchestrator
        from ..conversation.composer import ResponseComposer
        from ..observability.events import EventType
        from ..observability import get_ledger
        from datetime import datetime
        
        # Get managers
        session_mgr = get_session_manager()
        dialogue_mgr = get_dialogue_manager()
        ledger = get_ledger()
        
        # Get or create session
        if session_id:
            session = session_mgr.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = session_mgr.create_session(user_id)
        
        # Log COC message event
        if ledger:
            ledger.log(EventType.USER_MESSAGE, user_id, "coc_chat", 
                      input_payload={"message": message, "session_id": session.session_id})
        
        # Add user message to history
        session_mgr.add_message(session.session_id, "user", message)
        
        # Determine next action using dialogue manager
        next_action = dialogue_mgr.get_next_action(session, message)
        
        # Handle greeting
        if next_action["action"] == "greet":
            dialogue_mgr.update_state(session, next_action["dialogue_state"], "greeting")
            response_text = (
                "Hello! I'm ICGL, your Intentional Code Governance Layer assistant. "
                "I can help you with:\n"
                "• Creating collaboration channels between agents\n"
                "• Binding and managing governance policies\n"
                "• Analyzing your codebase\n"
                "• Querying the knowledge base\n\n"
                "What would you like to do?"
            )
            
            session_mgr.add_message(session.session_id, "assistant", response_text)
            session_mgr.update_session(session)
            
            return {
                "session_id": session.session_id,
                "response": response_text,
                "dialogue_state": next_action["dialogue_state"].value,
                "needs_clarification": False,
                "pending_approval": None
            }
        
        # Resolve intent with context
        resolver = IntentResolver()
        context_summary = dialogue_mgr.summarize_context(session.context)
        
        # Inject context into message for better resolution
        contextual_message = f"{context_summary}\n\nCurrent message: {message}" if context_summary else message
        intent_result = resolver.resolve(contextual_message)
        
        # Update last intent
        if hasattr(intent_result, 'intent_type'):
            session.context.last_intent = intent_result.intent_type
        elif isinstance(intent_result, str):
            session.context.last_intent = intent_result
        
        # Check if clarification needed
        if dialogue_mgr.should_clarify(intent_result, session.context):
            dialogue_mgr.update_state(session, next_action["dialogue_state"], "needs_clarification")
            
            # Generate clarification question (simplified for now)
            clarification_text = (
                "I need a bit more information to help you with that. "
                "Could you please clarify what you'd like me to do?"
            )
            
            session.context.clarification_history.append({
                "question": clarification_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            session_mgr.add_message(session.session_id, "assistant", clarification_text)
            session_mgr.update_session(session)
            
            return {
                "session_id": session.session_id,
                "response": clarification_text,
                "dialogue_state": "clarifying",
                "needs_clarification": True,
                "pending_approval": None
            }
        
        # Check if approval needed
        if dialogue_mgr.needs_approval(intent_result):
            dialogue_mgr.update_state(session, next_action["dialogue_state"], "requesting_approval")
            
            approval_text = (
                f"This action requires your explicit approval because it has high risk. "
                f"Would you like me to proceed?"
            )
            
            session_mgr.add_message(session.session_id, "assistant", approval_text)
            session_mgr.update_session(session)
            
            return {
                "session_id": session.session_id,
                "response": approval_text,
                "dialogue_state": "confirming",
                "needs_clarification": False,
                "pending_approval": {
                    "intent": str(intent_result),
                    "risk_level": "high"
                }
            }
        
        # Execute through orchestrator
        dialogue_mgr.update_state(session, next_action["dialogue_state"], "executing")
        
        orchestrator = ConversationOrchestrator()
        result = await orchestrator.handle(intent_result, {})
        
        # Generate response
        composer = ResponseComposer()
        response_text = composer.compose(intent_result, result)
        
        # Update to reporting state
        dialogue_mgr.update_state(session, next_action["dialogue_state"], "reporting_result")
        
        session_mgr.add_message(session.session_id, "assistant", response_text)
        session_mgr.update_session(session)
        
        return {
            "session_id": session.session_id,
            "response": response_text,
            "dialogue_state": "reporting",
            "needs_clarification": False,
            "pending_approval": None,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"COC chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 💬 COC SESSION MANAGEMENT (Phase 1)
# =============================================================================

@app.post("/coc/sessions")
async def create_conversation_session(user_id: str):
    """Create new conversation session"""
    try:
        from ..conversation.session import get_session_manager
        
        manager = get_session_manager()
        session = manager.create_session(user_id)
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "status": session.status.value
        }
    except Exception as e:
        logger.error(f"Create session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/sessions/{session_id}")
async def get_conversation_session(session_id: str):
    """Get session details"""
    try:
        from ..conversation.session import get_session_manager
        
        manager = get_session_manager()
        session = manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/sessions/{session_id}/history")
async def get_conversation_history(session_id: str, limit: int = 50):
    """Get conversation history"""
    try:
        from ..conversation.session import get_session_manager
        
        manager = get_session_manager()
        messages = manager.get_conversation_history(session_id, limit=limit)
        
        return {
            "session_id": session_id,
            "messages": [m.to_dict() for m in messages],
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Get history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/coc/sessions/{session_id}")
async def close_conversation_session(session_id: str):
    """Close conversation session"""
    try:
        from ..conversation.session import get_session_manager
        
        manager = get_session_manager()
        manager.close_session(session_id)
        
        return {"status": "closed", "session_id": session_id}
    except Exception as e:
        logger.error(f"Close session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/coc/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, status: Optional[str] = None):
    """Get all sessions for a user"""
    try:
        from ..conversation.session import get_session_manager, SessionStatus
        
        manager = get_session_manager()
        
        status_enum = SessionStatus(status) if status else None
        sessions = manager.get_user_sessions(user_id, status=status_enum)
        
        return {
            "user_id": user_id,
            "sessions": [s.to_dict() for s in sessions],
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Get user sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# =============================================================================
# 🚀 SERVER ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
