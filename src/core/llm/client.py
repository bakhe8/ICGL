from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMConfig:
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    json_mode: bool = False
    max_tokens: Optional[int] = None
    timeout: float = 60.0


class LLMClient:
    def __init__(self, config: Optional[LLMConfig] = None, *args, **kwargs):
        self.api_key: Optional[str] = None
        self.config = config or LLMConfig()

    async def acomplete(self, *args, **kwargs):
        return "Stubbed LLM response"

    async def generate_json(self, *args, **kwargs) -> tuple[dict, dict]:
        return {}, {"total_tokens": 0}

    async def generate_tests(self, code: str):
        return "Stubbed test generation report"

    async def analyze_code(self, code: str):
        return "Stubbed code analysis report"
