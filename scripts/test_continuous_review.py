"""
اختبار دورة المراجعة الدورية لإدارة التطوير
Test Continuous Development Review Cycle

Workflow:
1. DevelopmentManager reads all documents
2. Consults AI advisor (LLM)
3. Generates recommendations
4. Submits to HR for validation
5. HR escalates to CEO if needed
"""

import asyncio
from icgl.agents import DevelopmentManagerAgent
from icgl.kb import PersistentKnowledgeBase
from icgl.hr import WorkforceManager
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🔄 Testing Continuous Development Review Cycle...")
    
    # Initialize
    dev_manager = DevelopmentManagerAgent("DevelopmentManager")
    kb = PersistentKnowledgeBase()
    workforce = WorkforceManager()
    
    print("\n" + "="*80)
    print("🔄 دورة المراجعة الدورية - Continuous Review Cycle")
    print("="*80 + "\n")
    
    # Step 1: Periodic Document Review
    logger.info("📋 Step 1: Reading all documents...")
    review_report = await dev_manager.periodic_document_review(kb)
    
    print(f"Documents Reviewed: {len(review_report['documents_reviewed'])}")
    for doc in review_report['documents_reviewed']:
        print(f"  ✅ {doc}")
    
    print(f"\nAI Recommendations: {len(review_report['ai_recommendations'])}")
    for i, rec in enumerate(review_report['ai_recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Step 2: Submit to HR for validation
    logger.info("\n📤 Step 2: Submitting to HR Department...")
    
    # Create mock HR agent for validation
    class MockHRAgent:
        pass
    
    hr_agent = MockHRAgent()
    hr_validation = await dev_manager.submit_to_hr_for_validation(review_report, hr_agent)
    
    print(f"\n{hr_validation['review_summary']}")
    
    if hr_validation['escalate_to_ceo']:
        print("\n🚨 CEO APPROVAL REQUIRED:")
        for approval in hr_validation['approvals_needed']:
            print(f"  - {approval}")
    else:
        print("\n✅ No CEO approval needed - routine updates")
    
    print("\n" + "="*80)
    print("✅ Continuous Review Cycle Complete")
    print("="*80 + "\n")
    
    logger.info("✅ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
