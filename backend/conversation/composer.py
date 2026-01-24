class ResponseComposer:
    """
    Formats the conversation responses for the user.
    """

    def __init__(self):
        pass

    def compose_clarification(self, message: str) -> str:
        return f"🤔 **Clarification Required:** {message}"

    def compose_error(self, error: str) -> str:
        return f"⚠️ **System Error:** {error}"

    def compose_success(self, message: str) -> str:
        return f"✅ **Complete:** {message}"
