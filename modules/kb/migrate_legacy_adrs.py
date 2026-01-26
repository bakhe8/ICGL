"""
Migration Script: Legacy ADRs to Logic Kernel
=============================================
Migrates existing ADRs from PersistentKnowledgeBase (data/kb.db or bootstrap)
to structured JSON in backend/kb/kernel/*.json.

Extracts:
- Title
- Context
- Decision
- Status
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from modules.kb.persistent import PersistentKnowledgeBase


def migrate():
    project_root = Path(os.getcwd())
    kernel_dir = project_root / "backend" / "kb" / "kernel"
    kernel_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Starting Bootstrapped Migration to {kernel_dir}...")

    # Load KB (will bootstrap if empty)
    try:
        # Use simple args, assuming default db path is correct relative to cwd
        kb = PersistentKnowledgeBase(bootstrap=True)
        print(f"Loaded Knowledge Base with {len(kb.adrs)} ADRs.")
    except Exception as e:
        print(f"❌ Failed to load Knowledge Base: {e}")
        import traceback

        traceback.print_exc()
        return

    for adr_id, adr in kb.adrs.items():
        try:
            # Create JSON Structure specific for the Kernel
            adr_data = {
                "adr_id": adr.id,
                "title": adr.title,
                "decision": adr.decision,
                "context_summary": adr.context[:500] if adr.context else "",
                "full_context": adr.context,
                "status": adr.status,
                "timestamp": adr.created_at,
                "logical_impact": "LEGACY_MIGRATION",
                "governance_phase": 11,
                "migrated": True,
                "consequences": adr.consequences,
                "policies": adr.related_policies,
            }

            # Save to Kernel
            json_path = kernel_dir / f"{adr.id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(adr_data, f, indent=2)

            print(f"✅ Migrated: {adr.id}")

        except Exception as e:
            print(f"⚠️ Failed to migrate {adr_id}: {e}")

    print("🏁 Migration Complete.")


if __name__ == "__main__":
    migrate()
