"""
Consensus AI — Core LLM Infrastructure
=======================================

Defines the abstract interface for Large Language Model providers
and the concrete implementation for OpenAI.

Manifesto Reference:
- "Cycle 1: The Hitchhiker (Real Intelligence)"
- "Intelligence Layer must be pluggable and sovereign."
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import os

@dataclass
class LLMRequest:
    """Standardized request for LLM generation."""
    prompt: str
    system_prompt: str = "You are a helpful assistant."
    temperature: float = 0.7
    max_tokens: int = 2000
    stop_sequences: List[str] = field(default_factory=list)

@dataclass
class LLMResponse:
    """Standardized response from LLM."""
    content: str
    raw_response: Any = None
    usage: Dict[str, int] = field(default_factory=dict)
    provider: str = "unknown"

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generates text from the LLM."""
        pass

class MockProvider(LLMProvider):
    """
    Mock provider for testing or when no API key is present.
    """
    def __init__(self, fixed_response: str = None):
        self.fixed_response = fixed_response

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=self.fixed_response or f"[MOCK] Processed: {request.prompt[:50]}...",
            provider="mock"
        )

class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI API (GPT-4o, etc).
    Requires OPENAI_API_KEY environment variable.
    """
    def __init__(self, model: str = "gpt-4o", api_key: str = None):
        try:
            from openai import AsyncOpenAI
            self.model = model
            self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError("openai package is not installed. Run `pip install openai`.")
        except Exception as e:
            # Fallback handling or re-raise depending on strictness
            raise ValueError(f"Failed to initialize OpenAI client: {e}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop=request.stop_sequences if request.stop_sequences else None
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return LLMResponse(
                content=content,
                raw_response=response,
                usage=usage,
                provider="openai"
            )
        except Exception as e:
            return LLMResponse(
                content=f"Error generating response: {str(e)}",
                provider="openai-error"
            )
