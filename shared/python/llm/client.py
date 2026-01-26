from dataclasses import dataclass


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4"


class LLMClient:
    def __init__(self, config: LLMConfig = None, *args, **kwargs):
        pass

    async def acomplete(self, *args, **kwargs):
        return "Stubbed LLM response"

    async def generate_json(self, *args, **kwargs):
        return {}
