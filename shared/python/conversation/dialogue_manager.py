"""
Dialogue manager for advanced conversation flows.
Stub for ICGL dialogue logic.
"""

class DialogueManager:
    def get_next_action(self, session, message):
        return {"action": "greet", "dialogue_state": type("State", (), {"value": "greeting"})()}
    def update_state(self, session, state, reason):
        pass
    def summarize_context(self, context):
        return ""
    def should_clarify(self, intent_result, context):
        return False
    def needs_approval(self, intent_result):
        return False

def get_dialogue_manager():
    return DialogueManager()
