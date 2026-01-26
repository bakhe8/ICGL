import asyncio
import os
import sys

# Ensure we can import backend packages
sys.path.append(os.getcwd())

from modules.governance.committee import SovereignCommittee
from modules.governance.icgl import ICGL


async def main():
    print("🔮 [Reflection] STARTING SYSTEM REFLECTION CYCLE...")

    try:
        # Initialize Core
        icgl = ICGL()

        # Initialize Committee
        committee = SovereignCommittee(icgl)

        # Run the Session
        result = await committee.convene()

        print(f"\n✅ {result}")
        print("   The 'System Soul' has been captured in the UI.")

    except Exception as e:
        print(f"❌ Reflection Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
