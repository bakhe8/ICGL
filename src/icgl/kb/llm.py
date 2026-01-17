"""
LLM Interface Stub
------------------

Simple stub for LLM functionality used by COC.
This is a placeholder until full LLM integration is implemented.
"""

class SimpleLLM:
    """Simple LLM placeholder"""
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Placeholder for LLM generation.
        Returns simple responses for now.
        """
        # Simple rule-based responses for demo
        prompt_lower = prompt.lower()
        
        # Clarification questions
        if "clarify" in prompt_lower or "question" in prompt_lower:
            return "Could you please provide more details about what you'd like me to do?"
        
        # Entity extraction
        if "extract entities" in prompt_lower:
            return '{"agents": [], "policies": [], "channels": [], "actions": [], "times": [], "topics": []}'
        
        # Natural responses
        if "natural" in prompt_lower or "response" in prompt_lower:
            parts = prompt.split("Technical result:")
            if len(parts) > 1:
                result = parts[1].strip()
                if "Success: True" in result or "success" in result.lower():
                    return "Great! I've completed that action successfully. Everything is working as expected."
                elif "error" in result.lower() or "failed" in result.lower():
                    return "I encountered an issue while trying to do that. Let me know if you'd like me to try again or take a different approach."
                else:
                    return "I've processed your request. Let me know if you need anything else!"
        
        # Default
        return "I understand. Let me help you with that."


# Global LLM instance
_llm_instance = None

def get_llm() -> SimpleLLM:
    """Get global LLM instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = SimpleLLM()
    return _llm_instance
