from icgl.agents.architect import ArchitectAgent
from dotenv import load_dotenv

load_dotenv()

def verify_map():
    print("🔭 Testing Cycle 8: The Cartographer...")
    
    # 1. Init Agent
    agent = ArchitectAgent()
    
    # 2. Generate Prompt (which triggers Map Generation)
    prompt = agent.get_system_prompt()
    
    # 3. Inspect
    print("   Generated Prompt with Map (Snippet):")
    lines = prompt.splitlines()
    map_start = -1
    for i, line in enumerate(lines):
        if "REPOSITORY MAP" in line:
            map_start = i
            break
            
    if map_start != -1:
        snippet = "\n".join(lines[map_start:map_start+10])
        print(snippet)
        
        # 4. Assert
        if "src/" in prompt and "icgl/" in prompt:
            print("\n   ✅ VERIFIED: Map contains expected structure.")
        else:
             print("\n   ❌ Content Mismatch: Map seems empty or wrong.")
    else:
        print("\n   ❌ Failed: 'REPOSITORY MAP' header not found in prompt.")

if __name__ == "__main__":
    verify_map()
