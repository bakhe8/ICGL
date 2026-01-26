"""
ICGL LLM Client
===============

A robust, governed client for interacting with LLM providers (OpenAI).
Enforces:
- Timeouts
- Token limits
- JSON mode (where possible)
- Error handling
"""

import asyncio
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    from openai import AsyncOpenAI, OpenAIError
except ImportError:
    AsyncOpenAI = None
    OpenAIError = Exception


@dataclass
class LLMConfig:
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.0
    timeout: float = 30.0
    max_tokens: int = 1000
    json_mode: bool = True


class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.mock_mode = False
        if AsyncOpenAI and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            # Allow graceful degradation in dev/CI without keys.
            self.client = None
            self.mock_mode = True

    async def generate_json(
        self, system_prompt: str, user_prompt: str, config: LLMConfig = LLMConfig()
    ) -> Dict[str, Any]:
        """
        Generates a JSON response from the LLM.
        """
        if self.mock_mode:
            raise RuntimeError(
                "LLM unavailable; set OPENAI_API_KEY. No mock fallback allowed for governance mode."
            )
        if not self.client:
            raise ImportError("openai package not installed. Run `pip install openai`.")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        try:
            actual_system_prompt = system_prompt
            actual_user_prompt = user_prompt
            response_format = None
            if config.json_mode:
                response_format = {"type": "json_object"}
                if (
                    "json" not in actual_system_prompt.lower()
                    and "json" not in actual_user_prompt.lower()
                ):
                    actual_user_prompt += "\n\n(Return JSON format)"

            # Debug log for Phase 4 Sovereignty
            # print(f"--- LLM REQUEST (JSON MODE: {config.json_mode}) ---")
            # print(f"System: {actual_system_prompt[:100]}...")

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=config.model,
                    messages=[
                        {"role": "system", "content": actual_system_prompt},
                        {"role": "user", "content": actual_user_prompt},
                    ],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    response_format=response_format,
                ),
                timeout=config.timeout,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

            return json.loads(content), usage

        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM request timed out after {config.timeout}s")
        except json.JSONDecodeError:
            raise ValueError("LLM did not return valid JSON")
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected LLM Error: {str(e)}")

    async def get_embedding(
        self, text: str, model: str = "text-embedding-3-small"
    ) -> List[float]:
        """
        Generates an embedding vector for the given text.
        """
        if self.mock_mode:
            raise RuntimeError(
                "LLM unavailable; set OPENAI_API_KEY. No mock fallback allowed for embeddings."
            )
        if not self.client:
            raise ImportError("openai package not installed.")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        try:
            response = await asyncio.wait_for(
                self.client.embeddings.create(input=text, model=model), timeout=10.0
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Embedding Error: {str(e)}")
