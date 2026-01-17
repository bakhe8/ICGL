from icgl.agents.engineer import EngineerAgent
import os
import shutil
import time


def _safe_remove(path: str, retries: int = 5, delay_seconds: float = 0.2) -> bool:
    for attempt in range(1, retries + 1):
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except PermissionError:
            if attempt == retries:
                return False
            time.sleep(delay_seconds)
    return True

def verify_builder():
    print("👷 Testing Cycle 7: The Builder...")
    
    # 1. Initialize Engineer
    engineer = EngineerAgent(".")
    target_file = "hello_builder.py"
    target_content = "print('Hello from the Builder Agent! 🏗️')"
    
    # Clean up previous run
    if os.path.exists(target_file):
        if not _safe_remove(target_file):
            print(f"   ⚠️ Unable to delete '{target_file}' before test (file locked).")
        
    # 2. Request Write
    print(f"   Requesting write to '{target_file}'...")
    result = engineer.write_file(target_file, target_content)
    
    # 3. Verify
    if result == "Success" and os.path.exists(target_file):
        with open(target_file, "r") as f:
            content = f.read()
            if content == target_content:
                print(f"   ✅ VERIFIED: File exists with correct content.")
                
                # Cleanup
                if _safe_remove(target_file):
                    print("   🧹 Cleanup complete.")
                else:
                    print(f"   ⚠️ Cleanup skipped (file locked): {target_file}")
            else:
                print(f"   ❌ Content Mismatch: {content}")
    else:
        print(f"   ❌ Write Failed: {result}")

    # 4. Test Security (Path Traversal)
    print("   Testing Security (Path Traversal)...")
    res_sec = engineer.write_file("../malicious.txt", "attack")
    if "Security Violation" in res_sec:
        print("   ✅ Security Check Passed (Blocked traversal).")
    else:
        print(f"   ⚠️ Security Check FAILED: {res_sec}")

if __name__ == "__main__":
    verify_builder()
