import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("src"))
from icgl.conversation.intent_resolver import IntentResolver, ResolvedIntent
from icgl.conversation.dispatcher import ActionDispatcher, ConversationSession

# Mock ICGL Provider
class MockKB:
    def __init__(self):
        self.concepts = {}
        self.policies = {}
        self.adrs = {}

    def get_adr(self, adr_id):
        return self.adrs.get(adr_id)

    def add_adr(self, adr):
        self.adrs[adr.id] = adr

    def get_policy_by_code(self, code):
        return self.policies.get(code)

class MockICGL:
    def __init__(self):
        self.kb = MockKB()

class MockADR:
    def __init__(self, id):
        self.id = id
        self.related_policies = []
        self.title = "Test ADR"
        self.status = "DRAFT"

class MockPolicy:
    def __init__(self, id, code):
        self.id = id
        self.code = code

@pytest.fixture
def intent_resolver():
    return IntentResolver()

def test_intent_resolver_bind_policies(intent_resolver):
    # Test valid binding commands
    msg1 = "Link this decision to policy P-CORE-01"
    intent1 = intent_resolver.resolve(msg1)
    assert intent1.type == "bind_policies"
    assert intent1.params["codes"] == "P-CORE-01"

    msg2 = "Bind policies P-ARCH-99 and P-SEC-01 please"
    intent2 = intent_resolver.resolve(msg2)
    assert intent2.type == "bind_policies"
    assert "P-ARCH-99" in intent2.params["codes"]
    assert "P-SEC-01" in intent2.params["codes"]

    msg3 = "Analyze the policy P-CORE-01" 
    intent3 = intent_resolver.resolve(msg3)
    assert intent3.type == "run_analysis"

def test_dispatcher_bind_policies_sync_wrapper():
    asyncio.run(_test_dispatcher_bind_policies())

async def _test_dispatcher_bind_policies():
    # Setup
    icgl = MockICGL()
    
    # Pre-populate KB
    policy1 = MockPolicy("pol_1", "P-CORE-01")
    policy2 = MockPolicy("pol_2", "P-SEC-01")
    icgl.kb.policies["P-CORE-01"] = policy1
    icgl.kb.policies["P-SEC-01"] = policy2

    # Create Session & Active ADR
    adr = MockADR("adr_123")
    icgl.kb.add_adr(adr)
    
    session = ConversationSession(session_id="test_sess", last_adr_id="adr_123")
    
    # Init Dispatcher
    dispatcher = ActionDispatcher(lambda: icgl, None)

    # Execute Binding
    print("\nExecuting dispatcher.bind_policies...")
    result = await dispatcher.bind_policies(session, ["P-CORE-01", "P-SEC-01", "P-MISSING-99"], "user_1")
    print(f"Dispatcher Result: {result}")

    # Verify Result
    assert "P-CORE-01" in result["bound_policies"]
    assert "P-SEC-01" in result["bound_policies"]
    assert "P-MISSING-99" in result["unknown_codes"]
    
    # Verify ADR Update
    updated_adr = icgl.kb.get_adr("adr_123")
    assert "pol_1" in updated_adr.related_policies
    assert "pol_2" in updated_adr.related_policies
    assert len(updated_adr.related_policies) == 2
