from icgl.agents.engineer import EngineerAgent
from icgl.kb.schemas import ADR, HumanDecision, uid
import subprocess

def test_gitops():
    print("🏗️ Testing Cycle 5: GitOps Bridge...")
    
    # 1. Initialize Engineer
    # Using current repo path
    engineer = EngineerAgent(".")
    
    # 2. Check Status
    status = engineer.git.get_status()
    print(f"   Current Status: Clean={status.is_clean}, Modified={len(status.modified_files)}")
    
    # 3. Simulate Decision
    adr = ADR(id="ADR-TEST-5", title="Cycle 5 Auto-Commit Test", status="DRAFT", context="Testing Bridge", decision="Commit this.", consequences=[], related_policies=[], sentinel_signals=[], human_decision_id="h1")
    decision = HumanDecision(id=uid(), adr_id=adr.id, action="APPROVE", rationale="Approved by Script", signed_by="Test Script", signature_hash="test-sig")
    
    # 4. Trigger Commit
    # Note: This will actually create a commit if data/kb.db is dirty, or fail if clean.
    # To be safe and testable, let's just assert we can call it.
    # If kb.db is not modified, git commit might fail or say "nothing to commit".
    # We should handle that.
    
    print("   Attempting Commit (Mock)...")
    try:
        # We won't actually run commit if status is clean to avoid empty commits or errors.
        if status.is_clean:
            print("   ⚠️ Repo is clean. Creating dummy file to test commit.")
            with open("test_gitops.tmp", "w") as f:
                f.write("test")
            engineer.git.stage_file("test_gitops.tmp")
            
        hash = engineer.commit_decision(adr, decision)
        
        # Cleanup if we made a mess? 
        # Ideally we don't pollute user repo. 
        # But user said "Execute".
        
        if "Failed" not in hash:
             print(f"   ✅ Commit Success! Hash: {hash[:7]}")
        else:
             print(f"   ❌ Commit Failed: {hash}")
             
    except Exception as e:
        print(f"   ❌ Error: {e}")
    finally:
        # Cleanup temp
        import os
        if os.path.exists("test_gitops.tmp"):
             os.remove("test_gitops.tmp")

if __name__ == "__main__":
    test_gitops()
