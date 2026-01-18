"""
Test Proactive ArchivistAgent

This script demonstrates the enhanced ArchivistAgent capabilities:
1. Policy gap detection
2. LLM-powered policy generation
3. Document coherence checking
4. Automatic draft creation
"""

import asyncio
from icgl.agents.archivist_agent import ArchivistAgent
from icgl.kb import PersistentKnowledgeBase
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🏛️ Testing Proactive ArchivistAgent...")
    
    # Initialize
    archivist = ArchivistAgent("SovereignArchivist")
    kb = PersistentKnowledgeBase()
    
    # 1. Perform audit
    logger.info("\n📋 Step 1: Performing KB audit...")
    audit = await archivist.audit_kb(kb)
    print(f"\nAudit Results:")
    print(f"  Status: {audit['status']}")
    print(f"  Policies in KB: {audit['policies_count_kb']}")
    print(f"  Procedures: {audit['procedures_count']}")
    print(f"  Missing Policy Files: {audit['missing_policy_files']}")
    print(f"  Gaps: {audit['gaps']}")
    
    # 2. Check document coherence
    logger.info("\n🔍 Step 2: Checking document coherence...")
    coherence = await archivist.check_document_coherence(kb)
    print(f"\nCoherence Report:")
    print(f"  Status: {coherence['status']}")
    print(f"  Issues: {len(coherence['issues'])}")
    for issue in coherence['issues']:
        print(f"    - [{issue['severity']}] {issue['type']}: {issue['details']}")
    print(f"  Recommendations:")
    for rec in coherence['recommendations']:
        print(f"    - {rec}")
    
    # 3. Run full analysis (this will create missing policy files)
    logger.info("\n⚙️ Step 3: Running full analysis...")
    result = await archivist._analyze(None, kb)
    print(f"\nAnalysis Result:")
    print(f"  {result.analysis}")
    print(f"\nRecommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    logger.info("\n✅ ArchivistAgent test complete!")


if __name__ == "__main__":
    asyncio.run(main())
