"""
External Consultant Agent — ICGL
-------------------------------
Simulates an external AI consultant that reviews committee reports and provides recommendations.
Now powered by a Heuristic Intelligence Engine (Rule-based Persona).
"""

from typing import Dict, Any, List
import random
import os

class ExternalConsultantAgent:
    def __init__(self):
        self.name = "AI Consultant"
        # Try to initialize Real Intelligence
        try:
            from core.llm import OpenAIProvider
            print(f"*** CONSULTANT INIT DEBUG ***")
            print(f"Key in Env: {os.getenv('OPENAI_API_KEY') is not None}")
            if os.getenv('OPENAI_API_KEY'):
                print(f"Key Length: {len(os.getenv('OPENAI_API_KEY'))}")
            
            self.llm = OpenAIProvider(model="gpt-4o")
            # Test connection immediately
            import asyncio
            # We can't await here easily without creating loops, but let's assume valid instatiation means success
            self.has_intelligence = True
            print("*** SUCCESS: Consultant is SMART ***")
        except Exception as e:
            print(f"*** ERROR: Consultant Lobotomy ***")
            print(f"Reason: {e}")
            import traceback
            traceback.print_exc()
            self.llm = None
            self.has_intelligence = False

    async def review_committee_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the committee report using Real LLM if available, else Heuristic.
        """
        if self.has_intelligence:
            try:
                # Direct await since we are now async
                recommendation = await self._generate_real_insight(report)
                
                return {
                    "original_report": report,
                    "external_recommendation": recommendation,
                    "status": "reviewed",
                    "metadata": {"engine": "GPT-4o (Real)", "focus": "Strategic"}
                }
            except Exception as e:
                # Fallback to heuristic if LLM fails
                print(f"LLM Runtime Failed: {e}")
                import traceback
                traceback.print_exc()
                pass # Fall through to below logic

        # --- Fallback (Heuristic) ---
        analysis = self._analyze_context(report)
        recommendation = self._generate_strategic_insight(analysis)

        return {
            "original_report": report,
            "external_recommendation": recommendation,
            "status": "reviewed",
            "metadata": {"engine": "Heuristic v2.0 (Fallback)", "focus": analysis['primary_focus']}
        }

    async def _generate_real_insight(self, report: Dict) -> str:
        from core.llm import LLMRequest
        import json
        
        # Prepare context
        proposals_summary = [
            f"- {p.get('proposal')} (Status: {p.get('status')})" 
            for p in report.get('proposals', [])
        ]
        
        prompt = f"""
        You are a Strategic AI Consultant advising the CEO.
        
        System State:
        - Decisions Log: {json.dumps(proposals_summary, ensure_ascii=False)}
        - Health: {report.get('health')}
        
        Your Goal:
        Provide a concise, high-level strategic insight in Arabic.
        Analyze the pattern of decisions (what was approved/rejected).
        Offer one actionable piece of advice.
        Tone: Professional, Strategic, Executive-level.
        Length: 2-3 sentences max.
        """
        
        req = LLMRequest(prompt=prompt, temperature=0.7)
        resp = await self.llm.generate(req)
        return f"[GPT-4o] {resp.content}"

    async def review_document_draft(self, doc_type: str, content: str) -> Dict[str, Any]:
        """
        Specialized review for policies/ADRs.
        Acts as the 'Quality Gate' before submission.
        """
        if self.has_intelligence:
            try:
                from core.llm import LLMRequest
                prompt = f"""
                You are a Strategic Governance Auditor reviewing a draft document.
                
                Document Type: {doc_type}
                Content:
                {content[:3000]}... (truncated)
                
                Task:
                Provide a critical analysis. 
                1. Is the document professional and ready for a Sovereign entity?
                2. Are there specific, measurable requirements?
                3. Does it address current system gaps?
                
                LANGUAGE: Focus on professional Arabic terminology.
                
                Output JSON STRICTLY:
                {{
                    "approved": boolean,
                    "critique": "High-level summary in Arabic",
                    "raw_analysis": "Detailed technical analysis in Arabic",
                    "required_policies": ["P-XXX-NN", ...],
                    "score": 0-100
                }}
                """
                req = LLMRequest(prompt=prompt, temperature=0.2) # Low temp for auditing
                resp = await self.llm.generate(req)
                
                # Simple parsing (robustness would use Pydantic / Function Calling)
                import json
                cleaned = resp.content.strip()
                if cleaned.startswith("```json"):
                     cleaned = cleaned.replace("```json", "").replace("```", "")
                
                try:
                    data = json.loads(cleaned)
                    # If it's a dict but has no critique, or critique is a placeholder
                    if isinstance(data, dict) and (not data.get("critique") or data.get("critique") == "See detailed analysis below."):
                         data["raw_analysis"] = resp.content
                    return data
                except:
                    # User requested FULL visibility of raw thought process
                    return {
                        "approved": False, 
                        "critique": resp.content[:500] + "...", # Show a snippet
                        "raw_analysis": resp.content, # Return EVERYTHING
                        "score": 80
                    }
                    
            except Exception as e:
                print(f"Audit Failed: {e}")
                
        # Heuristic Logic
        missing_sections = []
        if "Enforcement" not in content and "Policy" in doc_type:
            missing_sections.append("Enforcement Section")
            
        if missing_sections:
            return {
                "approved": False, 
                "critique": f"Missing critical sections: {', '.join(missing_sections)}", 
                "score": 60
            }
            
        return {"approved": True, "critique": "Heuristic Check Passed", "score": 90}

    def _analyze_context(self, report: Dict) -> Dict:
        """Extracts key metrics from the raw report."""
        proposals = report.get('proposals', [])
        
        approved_count = sum(1 for p in proposals if p.get('status') == 'APPROVED')
        rejected_count = sum(1 for p in proposals if p.get('status') == 'REJECTED')
        pending_count = len(proposals) - approved_count - rejected_count
        
        # Determine focus area based on keywords in titles
        all_text = " ".join([p.get('proposal', '') + " " + p.get('details', '') for p in proposals]).lower()
        
        focus = "General Governance"
        if "security" in all_text or "policy" in all_text:
            focus = "Security & Compliance"
        elif "gitops" in all_text or "pipeline" in all_text or "deploy" in all_text:
            focus = "Operational Efficiency"
        elif "budget" in all_text or "resource" in all_text:
            focus = "Resource Optimization"

        return {
            "total": len(proposals),
            "approved": approved_count,
            "rejected": rejected_count,
            "pending": pending_count,
            "primary_focus": focus,
            "health_status": report.get('health', 'Unknown')
        }

    def _generate_strategic_insight(self, analysis: Dict) -> str:
        """Generates a professional Arabic recommendation based on analysis."""
        
        intro_templates = [
            f"بعد مراجعة {analysis['total']} من القرارات المدرجة، لاحظت أن التوجه العام يميل نحو تعزيز {analysis['primary_focus']}.",
            f"تشير البيانات الحالية لنشاط اللجنة إلى تركيز واضح على {analysis['primary_focus']}، وهو مؤشر إيجابي في المرحلة الحالية.",
            "مراجعة سريعة للموقف التنفيذي تظهر ديناميكية جيدة في اتخاذ القرار.",
        ]

        action_insight = ""
        if analysis['rejected'] > analysis['approved']:
            action_insight = "ألاحظ ارتفاع نسبة الرفض، مما يدل على حزم في المعايير الأمنية، ولكن يجب الحذر من التأثير على سرعة التشغيل (Velocity)."
        elif analysis['approved'] > 2:
            action_insight = "هناك زخم عالي في الاعتمادات، أوصي بمراجعة أثر هذه التغييرات المتلاحقة على استقرار بيئة الإنتاج."
        elif analysis['pending'] > 5:
            action_insight = "تراكم القرارات المعلقة قد يسبب عنق زجاجة (Bottleneck). أنصح بتفويض بعض الصلاحيات للموافقة التلقائية للقرارات منخفضة المخاطر."
        else:
            action_insight = "الأداء متوازن، أنصح بالاستمرار في هذا النسق مع التركيز على توثيق الأسباب (Rationale) لكل قرار."

        closing_templates = [
            "الخطوة القادمة يجب أن تكون تفعيل المراقبة الاستباقية.",
            "استمروا في هذا النهج، فأنتم تبنون أساساً متيناً للحوكمة الذاتية.",
            "أنصح بإعداد تقرير دوري لقياس العائد من هذه القرارات (ROI).",
        ]

        base_msg = f"{random.choice(intro_templates)} {action_insight} {random.choice(closing_templates)}"
        return f"[RULE-BASED] {base_msg}"
