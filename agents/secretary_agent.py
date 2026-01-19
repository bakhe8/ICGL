from typing import List, Optional, Dict, Any
from .base import Agent, AgentResult, Problem, AgentRole
from utils.logging_config import get_logger
from kb.schemas import now

class SecretaryAgent(Agent):
    """
    🏛️ CEO Executive Office (مكتب الرئيس التنفيذي)
    
    Responsibility: 
    First-tier decision-making office under direct CEO supervision.
    The always-open door for all employees.
    
    Core Functions:
    1. Open Door Policy - 24/7 access for all employees
    2. Bidirectional Translation - Arabic ↔ English
    3. Decision Making - Routine decisions autonomously
    4. Strategic Coordination - Between all departments
    5. Decision Relay - CEO decisions to all employees
    
    Authority Level: First-Tier Executive Office
    Reports To: CEO (Direct Supervision)
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, role=AgentRole.SECRETARY)
        self.decision_log = []
        self.translation_cache = {}
        self.open_requests = {}
    
    # ==================== OPEN DOOR POLICY ====================
    
    async def receive_employee_request(self, employee_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        الباب المفتوح - استقبال طلبات جميع الموظفين.
        
        Open Door - Receive requests from all employees 24/7.
        """
        request_id = f"REQ-{len(self.open_requests) + 1}"
        
        response = {
            "request_id": request_id,
            "status": "RECEIVED",
            "employee_id": employee_id,
            "timestamp": str(now()),
            "action": None
        }
        
        # Classify request
        if self._is_routine_request(request):
            # Handle immediately
            response["action"] = "HANDLED_IMMEDIATELY"
            response["decision"] = await self._make_routine_decision(request)
        else:
            # Escalate to CEO
            response["action"] = "ESCALATED_TO_CEO"
            response["escalation"] = await self._escalate_to_ceo(request)
        
        self.open_requests[request_id] = response
        return response
    
    def _is_routine_request(self, request: Dict[str, Any]) -> bool:
        """Determine if request is routine or strategic."""
        routine_types = [
            "status_update",
            "clarification",
            "translation",
            "coordination",
            "schedule"
        ]
        return request.get("type") in routine_types
    
    async def _make_routine_decision(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make routine decision autonomously."""
        decision = {
            "decision_type": "ROUTINE",
            "approved": True,
            "notes": "Handled by Executive Office",
            "timestamp": str(now())
        }
        
        self.decision_log.append(decision)
        return decision
    
    async def _escalate_to_ceo(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate strategic request to CEO."""
        escalation = {
            "escalated_to": "CEO",
            "reason": "Strategic decision required",
            "request_summary": request.get("summary", ""),
            "awaiting_decision": True
        }
        return escalation
    
    # ==================== TRANSLATION SERVICES ====================

    async def translate_event(self, event_type: str, actor: str, context: Dict[str, Any]) -> str:
        """
        ترجمة الأحداث التقنية للعربية.
        
        Translate technical events to Arabic for CEO.
        """
        mapping = {
            "agent.invoked": f"تم استدعاء الوكيل [{actor}] للبدء في تحليل المهمة.",
            "agent.responded": f"أتم الوكيل [{actor}] عمله بنجاح وقدم النتائج المطلوبة.",
            "policy.violated": f"🚨 تنبيه سيادي: تم رصد محاولة تجاوز للسياسة من قبل [{actor}]. تم الإيقاف فوراً.",
            "sentinel.alert": f"⚠️ إشعار أمني: رصد نظام Sentinel انحرافاً في معايير النظام.",
            "hdal.requested": "🏛️ في انتظار توقيعك السيادي للمضي قدماً في القرار.",
            "kb.write": f"تم تدوين معرفة جديدة في السجل التاريخي للنظام من قبل [{actor}].",
        }
        
        return mapping.get(event_type, f"حدث تقني: [{event_type}] بواسطة [{actor}]")
    
    async def translate_to_english(self, arabic_text: str) -> str:
        """
        ترجمة توجيهات الرئيس من العربية للإنجليزية الفنية.
        
        Translate CEO directives from Arabic to technical English.
        """
        # Check cache
        if arabic_text in self.translation_cache:
            return self.translation_cache[arabic_text]
        
        # Use LLM for translation if available
        if self.llm:
            try:
                from core.llm import LLMRequest
                prompt = f"""Translate the following Arabic text to technical English.
Preserve technical terms and context.

Arabic: {arabic_text}

English:"""
                request = LLMRequest(prompt=prompt, temperature=0.1, max_tokens=500)
                response = await self.llm.generate(request)
                
                translation = response.content.strip()
                self.translation_cache[arabic_text] = translation
                return translation
            except Exception as e:
                logger.error(f"Translation failed: {e}")
        
        # Fallback: return as-is with note
        return f"[Arabic] {arabic_text}"
    
    async def translate_to_arabic(self, english_text: str) -> str:
        """
        ترجمة التقارير الفنية للعربية الواضحة.
        
        Translate technical reports to clear Arabic for CEO.
        """
        # Check cache
        if english_text in self.translation_cache:
            return self.translation_cache[english_text]
        
        # Use LLM for translation if available
        if self.llm:
            try:
                from core.llm import LLMRequest
                prompt = f"""Translate the following technical English text to clear, professional Arabic.
Make it easy to understand for executive review.

English: {english_text}

Arabic:"""
                request = LLMRequest(prompt=prompt, temperature=0.1, max_tokens=500)
                response = await self.llm.generate(request)
                
                translation = response.content.strip()
                self.translation_cache[english_text] = translation
                return translation
            except Exception as e:
                logger.error(f"Translation failed: {e}")
        
        # Fallback: return as-is with note
        return f"[English] {english_text}"
    
    # ==================== DECISION RELAY ====================
    
    async def relay_ceo_decision(self, decision: Dict[str, Any], target_employees: List[str]) -> Dict[str, Any]:
        """
        توصيل قرارات الرئيس لجميع الموظفين.
        
        Relay CEO decisions to all employees with translation and clarification.
        """
        relay_result = {
            "decision_id": decision.get("id"),
            "relayed_to": target_employees,
            "timestamp": str(now()),
            "confirmations": []
        }
        
        # Translate decision if needed
        decision_text = decision.get("text", "")
        if decision.get("language") == "ar":
            decision_text_en = await self.translate_to_english(decision_text)
        else:
            decision_text_en = decision_text
        
        # Log relay
        logger.info(f"📢 Relaying CEO decision to {len(target_employees)} employees")
        
        return relay_result
    
    # ==================== COORDINATION ====================
    
    async def coordinate_departments(self, task: str, departments: List[str]) -> Dict[str, Any]:
        """
        تنسيق بين الإدارات.
        
        Coordinate between departments for task execution.
        """
        coordination = {
            "task": task,
            "departments": departments,
            "status": "COORDINATING",
            "timeline": "TBD"
        }
        
        logger.info(f"🔄 Coordinating task '{task}' across {len(departments)} departments")
        
        return coordination

    async def format_report_for_ceo(self, raw_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        تنسيق التقارير التقنية للرئيس.
        
        Format technical reports for CEO consumption.
        Translates, prioritizes, and polishes all agent reports.
        """
        formatted = {
            "from": "المكتب التنفيذي (CEO Executive Office)",
            "original_source": raw_report.get("from", "Unknown"),
            "to": "سيدي الرئيس",
            "timestamp": raw_report.get("timestamp"),
            "priority": raw_report.get("priority", "MEDIUM"),
            "summary_ar": "",
            "details": raw_report
        }
        
        # Generate Arabic summary based on report type
        if "audit" in raw_report:
            audit = raw_report["audit"]
            status_ar = {
                "HEALTHY": "سليم",
                "WARNING": "تحذير",
                "CRITICAL": "حرج"
            }.get(audit.get("status", "UNKNOWN"), "غير معروف")
            
            formatted["summary_ar"] = f"""
📜 تقرير الأرشيف السيادي

**الحالة:** {status_ar}
**السياسات في KB:** {audit.get('policies_count_kb', 0)}
**الإجراءات:** {audit.get('procedures_count', 0)}
**السياسات المفقودة:** {len(audit.get('missing_policy_files', []))}

"""
            if audit.get("gaps"):
                formatted["summary_ar"] += "**الثغرات المكتشفة:**\n"
                for gap in audit["gaps"]:
                    formatted["summary_ar"] += f"- {gap}\n"
        
        if "coherence" in raw_report:
            coherence = raw_report["coherence"]
            if coherence.get("issues"):
                formatted["summary_ar"] += "\n**مشاكل الترابط:**\n"
                for issue in coherence["issues"]:
                    formatted["summary_ar"] += f"- [{issue['severity']}] {issue['type']}\n"
        
        return formatted

    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        Internal analysis logic.
        """
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis="CEO Executive Office: Managing all employee communications and coordinating strategic decisions.",
            recommendations=["MAINTAIN_OPEN_DOOR_POLICY", "ENHANCE_TRANSLATION_SERVICES"],
            confidence=1.0
        )
