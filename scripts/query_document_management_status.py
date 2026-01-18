"""
استعلام عن وضع إدارة الوثائق
Query Document Management Department Status
"""

import asyncio
from icgl.agents import ArchivistAgent, SecretaryAgent
from icgl.kb import PersistentKnowledgeBase


async def main():
    # Initialize
    archivist = ArchivistAgent("SovereignArchivist")
    secretary = SecretaryAgent("SovereignSecretary")
    kb = PersistentKnowledgeBase()
    
    # Get report through proper channels
    report = await archivist.submit_report_to_ceo(kb, secretary)
    
    # Display formatted report
    print("\n" + "="*80)
    print("📬 تقرير إدارة الوثائق والسياسات")
    print("="*80)
    print(f"\nمن: {report['from']}")
    print(f"المصدر: {report['original_source']}")
    print(f"الأولوية: {report['priority']}")
    print(f"\n{report['summary_ar']}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
