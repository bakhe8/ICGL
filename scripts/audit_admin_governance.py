from icgl.governance.admin_guard import AdministrationGuard
from icgl.agents.secretary_agent import SecretaryAgent

def test_guard():
    print("🚀 Running AdministrationGuard Verification...")
    
    # 1. Test Agent Integrity (SecretaryAgent should be PERFECT)
    issues = AdministrationGuard.validate_agent_integrity(SecretaryAgent)
    print(f"Secretary Health Status: {'✅ PERFECT' if not issues else '❌ ISSUES FOUND: ' + str(issues)}")
    
    # 2. Test Environment Sync (Violation detection)
    bad_cmd = "npm install && npm start"
    env_issues = AdministrationGuard.check_environment_sync(bad_cmd)
    print(f"Environment Check (Bad Command): {'❌ VIOLATION DETECTED' if env_issues else '✅ PASSED'}")
    if env_issues:
        print(f"   Reason: {env_issues[0]}")
        
    # 3. Test Environment Sync (Pass detection)
    good_cmd = "npm install; npm start"
    env_issues_good = AdministrationGuard.check_environment_sync(good_cmd)
    print(f"Environment Check (Good Command): {'✅ PASSED' if not env_issues_good else '❌ FAILED'}")

if __name__ == "__main__":
    test_guard()
