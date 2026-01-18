"""
Sovereign Governance Review
============================

Submits all policies, procedures, and ADRs to the Advisory Hub (LLM)
for comprehensive analysis and recommendations.

Output: Detailed report with AI suggestions for the CEO to review.
"""

import asyncio
from icgl.kb import PersistentKnowledgeBase
from icgl.core.llm import OpenAIProvider
from icgl.utils.logging_config import get_logger
import os

logger = get_logger(__name__)


async def review_governance_documents():
    """
    Comprehensive governance review process.
    
    Steps:
    1. Load all policies, procedures, ADRs from KB
    2. Submit to LLM for analysis
    3. Generate recommendations
    4. Create report for CEO
    """
    
    logger.info("🏛️ Starting Sovereign Governance Review...")
    
    # 1. Initialize
    kb = PersistentKnowledgeBase()
    llm = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 2. Collect all governance documents
    logger.info("📚 Collecting governance documents...")
    
    policies = list(kb.policies.values())
    procedures = list(kb.procedures.values()) if hasattr(kb, 'procedures') else []
    adrs = list(kb.adrs.values())
    
    logger.info(f"   Found: {len(policies)} policies, {len(procedures)} procedures, {len(adrs)} ADRs")
    
    # 3. Prepare comprehensive context
    context = f"""
# Sovereign Governance Review Request

You are reviewing the governance framework of the ICGL system on behalf of the CEO.

## Current Governance Documents

### Policies ({len(policies)}):
"""
    
    for policy in policies:
        context += f"\n**{policy.code}**: {policy.title}\n"
        context += f"Rule: {policy.rule}\n"
        context += f"Severity: {policy.severity}\n\n"
    
    context += f"\n### Procedures ({len(procedures)}):\n"
    for proc in procedures:
        context += f"\n**{proc.code}**: {proc.title}\n"
        context += f"Type: {proc.type}\n"
        context += f"Steps: {len(proc.steps)}\n\n"
    
    context += f"\n### ADRs ({len(adrs)}):\n"
    for adr in adrs:
        context += f"\n**{adr.title}**\n"
        context += f"Status: {adr.status}\n"
        context += f"Context: {adr.context[:200]}...\n\n"
    
    # 4. Submit to LLM for analysis
    logger.info("🤖 Submitting to Advisory Hub (LLM) for analysis...")
    
    prompt = context + """

## Analysis Request

Please provide a comprehensive review with:

1. **Strengths**: What is working well in the current governance framework?
2. **Gaps**: What critical policies or procedures are missing?
3. **Conflicts**: Are there any contradictions between documents?
4. **Recommendations**: Specific, actionable improvements prioritized by impact
5. **Risk Assessment**: What governance risks exist?

Format your response as a structured report suitable for executive review.
"""
    
    try:
        from icgl.core.llm import LLMRequest
        
        request = LLMRequest(
            prompt=prompt,
            temperature=0.3,  # Lower temperature for analytical work
            max_tokens=4000
        )
        
        response = await llm.generate(request)
        
        # 5. Save report
        report_path = "docs/REPORTS/GOVERNANCE_REVIEW_2026-01-17.md"
        
        report_content = f"""# 🏛️ Sovereign Governance Review Report

**Date:** 2026-01-17  
**Requested by:** Office of the CEO  
**Reviewed by:** Advisory Hub (AI Analysis)

---

## Executive Summary

This report presents a comprehensive analysis of the ICGL governance framework, including all policies, procedures, and architectural decisions.

**Documents Reviewed:**
- {len(policies)} Policies
- {len(procedures)} Procedures
- {len(adrs)} ADRs

---

## AI Analysis & Recommendations

{response.content}

---

## Next Steps

The CEO should review these recommendations and issue sovereign decisions on:
1. Which gaps to address immediately
2. Which policies require updates
3. Which new procedures to establish

---

**This is an advisory report. All decisions remain with the sovereign authority.**
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"✅ Governance review complete!")
        logger.info(f"📄 Report saved to: {report_path}")
        
        print("\n" + "="*80)
        print("🏛️ SOVEREIGN GOVERNANCE REVIEW COMPLETE")
        print("="*80)
        print(f"\n📊 Documents Analyzed:")
        print(f"   - {len(policies)} Policies")
        print(f"   - {len(procedures)} Procedures")
        print(f"   - {len(adrs)} ADRs")
        print(f"\n📄 Full Report: {report_path}")
        print("\n" + "="*80)
        
        return report_path
        
    except Exception as e:
        logger.error(f"❌ Review failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(review_governance_documents())
