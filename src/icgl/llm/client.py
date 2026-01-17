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

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 🔴 MANDATORY: Load Environment FIRST (same as cli.py)
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

import json
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

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

    async def generate_json(self, 
                            system_prompt: str, 
                            user_prompt: str, 
                            config: LLMConfig = LLMConfig()) -> Dict[str, Any]:
        """
        Generates a JSON response from the LLM.
        """
        if self.mock_mode:
            raise RuntimeError("LLM unavailable; set OPENAI_API_KEY. No mock fallback allowed for governance mode.")
        if not self.client:
            raise ImportError("openai package not installed. Run `pip install openai`.")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        try:
            response_format = {"type": "json_object"} if config.json_mode else None
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=config.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    response_format=response_format
                ),
                timeout=config.timeout
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
                
            return json.loads(content)
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM request timed out after {config.timeout}s")
        except json.JSONDecodeError:
            raise ValueError("LLM did not return valid JSON")
        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected LLM Error: {str(e)}")

    async def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generates an embedding vector for the given text.
        """
        if self.mock_mode:
            raise RuntimeError("LLM unavailable; set OPENAI_API_KEY. No mock fallback allowed for embeddings.")
        if not self.client:
            raise ImportError("openai package not installed.")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
            
        try:
            response = await asyncio.wait_for(
                self.client.embeddings.create(
                    input=text,
                    model=model
                ),
                timeout=10.0
            )
            return response.data[0].embedding
        except Exception as e:
             raise RuntimeError(f"Embedding Error: {str(e)}")
