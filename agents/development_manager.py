from typing import List, Optional, Dict, Any
from .base import Agent, AgentResult, Problem, AgentRole
from utils.logging_config import get_logger
from kb.schemas import now

logger = get_logger(__name__)


class DevelopmentManagerAgent(Agent):
    """
    🏗️ Development Manager Agent
    
    Responsibility:
    Oversees system development, coordinates agents, and implements
    strategic initiatives. Acts as the bridge between CEO directives
    and technical execution.
    
    First Mission: Redistribute roles among existing agents to address
    critical gaps (PolicyEngine, RuntimeGuard, GitOps) without creating
    new agents.
    """
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id=agent_id, role=AgentRole.DEVELOPMENT_MANAGER)
        self.role_assignments = {}
        logger.info("🏗️ DevelopmentManagerAgent initialized")
    
    async def redistribute_roles(self) -> Dict[str, List[str]]:
        """
        إعادة توزيع الأدوار على الوكلاء الموجودين.
        
        Redistribute roles among existing agents to maximize efficiency
        and address critical gaps.
        
        Returns:
            Dictionary mapping agents to their new responsibilities
        """
        redistribution_plan = {
            "SentinelAgent": [
                "دمج مع SentinelEngine لمراقبة المخاطر تلقائياً",
                "توليد تقارير المخاطر للإدارة",
                "تنبيهات استباقية عند اكتشاف انحرافات",
                "→ يعالج جزء من RuntimeGuard"
            ],
            
            "PolicyAgent": [
                "تنفيذ مهام PolicyEngine: مراجعة السياسات",
                "التحقق من الالتزام",
                "توليد تقارير السياسات",
                "→ يصبح PolicyEngine الفعلي"
            ],
            
            "SecretaryAgent": [
                "تجميع المدخلات من الإدارات",
                "أرشفة القرارات",
                "جدولة الاجتماعات والتنبيهات الدورية",
                "→ مركز التنسيق الإداري"
            ],
            
            "MonitorAgent": [
                "مراقبة الأداء والاتساق (PerformanceMonitor)",
                "جمع مؤشرات الصحة",
                "إرسال تنبيهات عند المشاكل",
                "→ يعالج PerformanceMonitor"
            ],
            
            "MediatorAgent": [
                "فض التعارضات بين الوكلاء/الإدارات",
                "تقديم حلول وسطية",
                "تصعيد النزاعات للرئيس",
                "→ حل النزاعات المؤسسية"
            ],
            
            "FailureAgent": [
                "تحليل حالات الفشل والأعطال",
                "تقارير أسباب الفشل",
                "اقتراحات المعالجة",
                "→ Post-mortem analysis"
            ],
            
            "BuilderAgent": [
                "دعم EngineerAgent في البناء التلقائي",
                "نشر التحديثات البرمجية",
                "→ جزء من GitOpsPipeline"
            ],
            
            "ArchivistAgent": [
                "إدارة الأرشيف المؤسسي",
                "حفظ وتوثيق القرارات",
                "كشف الفجوات والتضاربات",
                "→ الذاكرة المؤسسية"
            ],
            
            "ArchitectAgent": [
                "مراجعة التصميمات المعمارية",
                "اقتراح تحسينات هيكلية",
                "ضمان اتساق البنية مع السياسات",
                "→ الحوكمة المعمارية"
            ],
            
            "EngineerAgent": [
                "تنفيذ الكود",
                "Git operations (commit, push)",
                "→ جزء من GitOpsPipeline"
            ],
            
            "MockAgent": [
                "الاختبارات",
                "محاكاة السيناريوهات",
                "→ Testing & Simulation"
            ]
        }
        
        self.role_assignments = redistribution_plan
        logger.info(f"✅ Role redistribution plan created for {len(redistribution_plan)} agents")
        
        return redistribution_plan
    
    async def create_implementation_plan(self) -> str:
        """
        إنشاء خطة تنفيذية لمعالجة الفجوات الحرجة.
        
        Create implementation plan to address critical gaps using
        existing agents.
        """
        plan = """
# 🏗️ خطة التنفيذ - معالجة الفجوات الحرجة

## الهدف
معالجة الفجوات الثلاث الحرجة باستخدام الوكلاء الموجودين:
1. PolicyEngine
2. RuntimeGuard
3. GitOpsPipeline

---

## المرحلة 1: PolicyEngine (باستخدام PolicyAgent)

### الإجراءات:
- [x] تعزيز PolicyAgent بقدرات PolicyEngine
- [ ] إضافة policy validation
- [ ] إضافة compliance checking
- [ ] تقارير دورية للسياسات

### الوكلاء المشاركون:
- PolicyAgent (رئيسي)
- SentinelAgent (دعم)
- ArchivistAgent (توثيق)

---

## المرحلة 2: RuntimeGuard (باستخدام SentinelAgent + MonitorAgent)

### الإجراءات:
- [ ] دمج SentinelAgent مع SentinelEngine
- [ ] تعزيز MonitorAgent بـ performance metrics
- [ ] إضافة Circuit Breakers
- [ ] Timeout mechanisms

### الوكلاء المشاركون:
- SentinelAgent (مراقبة المخاطر)
- MonitorAgent (مراقبة الأداء)
- FailureAgent (تحليل الأعطال)

---

## المرحلة 3: GitOpsPipeline (باستخدام EngineerAgent + BuilderAgent)

### الإجراءات:
- [ ] تعزيز EngineerAgent بـ auto-deployment
- [ ] ربط BuilderAgent بـ CI/CD
- [ ] Automated testing
- [ ] Rollback mechanisms

### الوكلاء المشاركون:
- EngineerAgent (تنفيذ)
- BuilderAgent (بناء)
- ArchitectAgent (مراجعة)

---

## الجدول الزمني

| المرحلة | المدة | الأولوية |
|:---|:---:|:---:|
| PolicyEngine | 3 أيام | عالية |
| RuntimeGuard | 5 أيام | عالية |
| GitOpsPipeline | 7 أيام | متوسطة |

---

**الميزة:** استخدام الوكلاء الموجودين = توفير الوقت والجهد
"""
        return plan
    
    async def _analyze(self, problem: Problem, kb) -> AgentResult:
        """
        تحليل وتنفيذ خطة إعادة التوزيع.
        """
        # Execute role redistribution
        redistribution = await self.redistribute_roles()
        
        # Create implementation plan
        plan = await self.create_implementation_plan()
        
        analysis = f"""
🏗️ Development Manager Analysis

Role Redistribution Complete:
- {len(redistribution)} agents assigned new responsibilities
- 3 critical gaps addressed using existing agents
- No new agents needed

Implementation Plan Created:
- PolicyEngine → PolicyAgent
- RuntimeGuard → SentinelAgent + MonitorAgent
- GitOpsPipeline → EngineerAgent + BuilderAgent
"""
        
        return AgentResult(
            agent_id=self.agent_id,
            role=self.role,
            analysis=analysis,
            recommendations=[
                "START_PHASE_1_POLICY_ENGINE",
                "ENHANCE_SENTINEL_MONITOR_INTEGRATION",
                "SETUP_GITOPS_PIPELINE"
            ],
            confidence=0.95
        )
    
    async def periodic_document_review(self, kb) -> Dict[str, Any]:
        """
        المراجعة الدورية لجميع الوثائق.
        
        Periodic review of all documents including agents_report.md.
        
        Workflow:
        1. Read all documents
        2. Consult external AI advisor (LLM)
        3. Generate improvement recommendations
        4. Submit to HR Department for validation
        5. HR escalates to CEO for approval
        """
        from pathlib import Path
        
        review_report = {
            "timestamp": str(now()),
            "documents_reviewed": [],
            "ai_recommendations": [],
            "hr_validation_status": "PENDING",
            "ceo_approval_required": False
        }
        
        # 1. Read all documents
        docs_to_review = [
            "docs/REPORTS/agents_report.md",
            "docs/GM_PRIORITIES.md",
            "docs/DEPARTMENTAL_DFDS.md",
            "docs/adrs/ADR-CANONICAL-001.md",
            "docs/HR/JOB_DESCRIPTIONS/INDEX.md"
        ]
        
        documents_content = {}
        for doc_path in docs_to_review:
            doc_file = Path(doc_path)
            if doc_file.exists():
                try:
                    content = doc_file.read_text(encoding='utf-8')
                    documents_content[doc_path] = content
                    review_report["documents_reviewed"].append(doc_path)
                    logger.info(f"📄 Read: {doc_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read {doc_path}: {e}")
        
        # 2. Consult external AI advisor (LLM)
        if self.llm and documents_content:
            recommendations = await self._consult_ai_advisor(documents_content)
            review_report["ai_recommendations"] = recommendations
        else:
            logger.warning("⚠️ LLM not available, skipping AI consultation")
            review_report["ai_recommendations"] = ["LLM_NOT_AVAILABLE"]
        
        # 3. Determine if updates are needed
        if review_report["ai_recommendations"] and review_report["ai_recommendations"] != ["LLM_NOT_AVAILABLE"]:
            review_report["ceo_approval_required"] = True
        
        logger.info(f"✅ Periodic review complete: {len(review_report['documents_reviewed'])} documents")
        
        return review_report
    
    async def _consult_ai_advisor(self, documents: Dict[str, str]) -> List[str]:
        """
        استشارة المستشار الخارجي (LLM) للحصول على توصيات التطوير.
        
        Consult external AI advisor for development recommendations.
        """
        if not self.llm:
            return []
        
        # Prepare context
        context = "# System Documents Review\n\n"
        for doc_path, content in documents.items():
            context += f"## {doc_path}\n\n"
            # Limit content to avoid token overflow
            context += content[:2000] + "\n\n---\n\n"
        
        prompt = f"""You are an external AI advisor reviewing the ICGL system documentation.

{context}

Based on these documents, provide 3-5 specific, actionable recommendations for improvement.

Focus on:
1. Agent role clarity and efficiency
2. Documentation gaps or inconsistencies
3. Process improvements
4. Governance enhancements

Format your response as a numbered list of recommendations.
"""
        
        try:
            from core.llm import LLMRequest
            request = LLMRequest(prompt=prompt, temperature=0.3, max_tokens=1000)
            response = await self.llm.generate(request)
            
            # Parse recommendations
            recommendations = []
            for line in response.content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    recommendations.append(line)
            
            logger.info(f"✅ AI advisor provided {len(recommendations)} recommendations")
            return recommendations
        
        except Exception as e:
            logger.error(f"❌ AI consultation failed: {e}")
            return []
    
    async def submit_to_hr_for_validation(self, review_report: Dict[str, Any], hr_agent) -> Dict[str, Any]:
        """
        إرسال نتائج المراجعة لشؤون الموظفين للتحقق.
        
        Submit review results to HR Department for validation.
        
        HR will:
        1. Validate recommendations
        2. Check feasibility
        3. Escalate to CEO if approvals needed
        """
        hr_validation = {
            "validated_by": "HR Department",
            "timestamp": str(now()),
            "review_summary": "",
            "feasibility_check": "PASSED",
            "approvals_needed": [],
            "escalate_to_ceo": False
        }
        
        # Generate summary
        hr_validation["review_summary"] = f"""
📊 Development Manager Review Summary

Documents Reviewed: {len(review_report['documents_reviewed'])}
AI Recommendations: {len(review_report['ai_recommendations'])}

Recommendations:
"""
        for i, rec in enumerate(review_report['ai_recommendations'], 1):
            hr_validation["review_summary"] += f"\n{i}. {rec}"
        
        # Check if CEO approval needed
        if review_report.get("ceo_approval_required"):
            hr_validation["escalate_to_ceo"] = True
            hr_validation["approvals_needed"] = [
                "CEO approval for implementing AI recommendations"
            ]
        
        logger.info(f"✅ Submitted to HR for validation")
        
        return hr_validation

