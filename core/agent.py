import os
import json
import time
import asyncio
import threading
from typing import List, Dict, Any, Optional
import litellm
from pathlib import Path

# ── Multi-model fallback chain ──────────────────────────────────────────────
FALLBACK_MODELS = [
    "openrouter/anthropic/claude-3.5-sonnet",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free",
    "openrouter/deepseek/deepseek-chat:free",
    "openrouter/qwen/qwen-2.5-72b-instruct:free",
    "openrouter/google/gemini-2.0-flash-exp:free",
]

class CyraAgent:
    def __init__(self, model: str = "openrouter/anthropic/claude-3.5-sonnet",
                 api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        litellm.drop_params = True

    def _build_params(self, messages: List[Dict], tools=None) -> dict:
        params = {
            "model": self.model,
            "messages": messages,
            "api_key": self.api_key,
            "extra_headers": {
                "HTTP-Referer": "http://localhost:8200",
                "X-Title": "Cyra-OS"
            }
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"
        return params

    async def chat(self, messages: List[Dict[str, str]],
                   tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Unified chat with multi-model fallback."""
        if not self.api_key:
            return {"error": "Missing OpenRouter API Key. Set it in Dashboard or .env."}

        # Build ordered model list: current first, then fallbacks
        models_to_try = [self.model]
        for m in FALLBACK_MODELS:
            if m != self.model and m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model_id in models_to_try:
            try:
                params = self._build_params(messages, tools)
                params["model"] = model_id
                response = await litellm.acompletion(**params)
                if model_id != self.model:
                    print(f"[CyraAgent] Fallback succeeded with {model_id}")
                return response
            except Exception as e:
                last_error = e
                print(f"[CyraAgent] Model {model_id} failed: {e}")
                continue

        return {"error": f"All models failed. Last error: {last_error}"}

    async def chat_stream(self, messages: List[Dict[str, str]],
                          tools=None):
        """Streaming chat — yields chunks for SSE."""
        if not self.api_key:
            yield {"error": "Missing OpenRouter API Key."}
            return

        models_to_try = [self.model]
        for m in FALLBACK_MODELS:
            if m != self.model and m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for model_id in models_to_try:
            try:
                params = self._build_params(messages, tools)
                params["model"] = model_id
                params["stream"] = True
                response = await litellm.acompletion(**params)
                async for chunk in response:
                    yield {"chunk": chunk}
                return
            except Exception as e:
                last_error = e
                print(f"[CyraAgent] Stream model {model_id} failed: {e}")
                continue

        yield {"error": f"All models failed. Last error: {last_error}"}

    def switch_model(self, new_model: str):
        self.model = new_model
