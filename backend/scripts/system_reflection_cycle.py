import asyncio
import os
import sys

# Ensure we can import backend packages
sys.path.append(os.getcwd())

<<<<<<< HEAD
from modules.governance.committee import SovereignCommittee
from modules.governance.icgl import ICGL
=======
from shared.python.governance_shared.governance.committee import SovereignCommittee
from shared.python.governance_shared.governance.icgl import ICGL
>>>>>>> 1017ee5d6165b6b836bcf8f4a86dd3b8c5d9a8a4


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
