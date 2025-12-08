from __future__ import annotations

import os
from typing import List, Dict, Any

from openai import OpenAI


class OpenAIClient:
    def __init__(self, api_key: str, model: str):
        # The official SDK reads from env as well, but we pass explicitly
        os.environ.setdefault("OPENAI_API_KEY", api_key)
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int | None = None) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""

