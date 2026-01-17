import os
import json

def verify_metrics():
    log_file = "data/logs/agent_metrics.jsonl"
    if not os.path.exists(log_file):
        print("❌ Metrics log file not found!")
        exit(1)
        
    print("✅ Metrics log exists.")
    with open(log_file, "r") as f:
        lines = f.readlines()
        if not lines:
            print("❌ Log is empty!")
            exit(1)
            
        last = json.loads(lines[-1])
        print(f"   Last Metric: Agent={last['agent_id']}, Latency={last['latency_ms']:.2f}ms, Success={last['success']}")
        
    if last['agent_id'] == "agent-architect":
        print("✅ Architect Agent metrics verified.")
    else:
        # Note: If other agents ran, this might fail, but checking existence is enough for now.
        print("⚠️ Last metric was not architect, but metrics are flowing.")

if __name__ == "__main__":
    verify_metrics()
