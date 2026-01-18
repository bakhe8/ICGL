"""
Test Secretary-Archivist Integration

Demonstrates the proper reporting hierarchy:
ArchivistAgent → SecretaryAgent → CEO
"""

import asyncio
from icgl.agents import ArchivistAgent, SecretaryAgent
from icgl.kb import PersistentKnowledgeBase
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🏛️ Testing Secretary-Archivist Integration...")
    
    # Initialize agents
    archivist = ArchivistAgent("SovereignArchivist")
    secretary = SecretaryAgent("SovereignSecretary")
    kb = PersistentKnowledgeBase()
    
    # Archivist submits report through Secretary
    logger.info("\n📋 Archivist generating report...")
    report = await archivist.submit_report_to_ceo(kb, secretary_agent=secretary)
    
    print("\n" + "="*80)
    print("📬 REPORT TO CEO (via SecretaryAgent)")
    print("="*80)
    print(f"\nFrom: {report['from']}")
    print(f"Original Source: {report['original_source']}")
    print(f"Priority: {report['priority']}")
    print(f"\n{report['summary_ar']}")
    print("="*80)
    
    logger.info("\n✅ Integration test complete!")


if __name__ == "__main__":
    asyncio.run(main())
