import os
import json
from icgl.core.observability import SystemObserver
from icgl.kb.schemas import uid

def test_intervention_logging():
    print("👁️ Testing Observability Layer...")
    
    # 1. Init Observer
    observer = SystemObserver() # defaults to data/logs
    
    # 2. Simulate Intervention
    fake_adr_id = uid()
    print(f"   Simulating Rejection for ADR {fake_adr_id}...")
    
    observer.record_intervention(
        adr_id=fake_adr_id,
        original_rec="APPROVE",
        action="REJECT",
        reason="Testing Observability Logic"
    )
    
    # 3. Verify Log
    log_file = "data/logs/interventions.jsonl"
    if not os.path.exists(log_file):
        print("❌ Log file not created!")
        exit(1)
        
    print("   ✅ Log file exists.")
    
    with open(log_file, "r") as f:
        lines = f.readlines()
        last_line = lines[-1]
        data = json.loads(last_line)
        
    if data["adr_id"] == fake_adr_id and data["reason"] == "Testing Observability Logic":
        print("   ✅ Log content verified.")
    else:
        print(f"❌ Log content mismatch: {data}")
        exit(1)

if __name__ == "__main__":
    test_intervention_logging()
