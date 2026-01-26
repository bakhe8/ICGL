class ConversationOrchestrator:
    def __init__(self, get_engine_fn, run_task_fn):
        self.composer = self

    async def handle(self, request):
        from ..chat.schemas import ChatResponse

        return ChatResponse(messages=[{"role": "assistant", "content": "System is recovering..."}])

    def error(self, msg):
        return {"error": msg}
