"""
تفعيل وكيل إدارة التطوير
Activate Development Manager Agent

First mission: Redistribute roles among existing agents
"""

import asyncio
from icgl.agents import DevelopmentManagerAgent, SecretaryAgent
from icgl.kb import PersistentKnowledgeBase
from icgl.utils.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🏗️ Activating Development Manager Agent...")
    
    # Initialize
    dev_manager = DevelopmentManagerAgent("DevelopmentManager")
    secretary = SecretaryAgent("SovereignSecretary")
    kb = PersistentKnowledgeBase()
    
    # Execute first mission: Role redistribution
    logger.info("\n📋 Mission 1: Role Redistribution")
    redistribution = await dev_manager.redistribute_roles()
    
    print("\n" + "="*80)
    print("🏗️ خطة إعادة توزيع الأدوار")
    print("Role Redistribution Plan")
    print("="*80 + "\n")
    
    for agent, responsibilities in redistribution.items():
        print(f"**{agent}:**")
        for resp in responsibilities:
            print(f"  - {resp}")
        print()
    
    # Create implementation plan
    logger.info("\n📝 Creating Implementation Plan...")
    plan = await dev_manager.create_implementation_plan()
    
    # Save plan
    plan_file = "docs/REPORTS/ROLE_REDISTRIBUTION_PLAN.md"
    with open(plan_file, 'w', encoding='utf-8') as f:
        f.write(plan)
    
    logger.info(f"✅ Implementation plan saved to: {plan_file}")
    
    # Run analysis
    result = await dev_manager._analyze(None, kb)
    
    print("\n" + "="*80)
    print("📊 Development Manager Analysis")
    print("="*80)
    print(result.analysis)
    print("\n**Recommendations:**")
    for rec in result.recommendations:
        print(f"  - {rec}")
    print("="*80 + "\n")
    
    logger.info("✅ Development Manager activated successfully!")


if __name__ == "__main__":
    asyncio.run(main())
