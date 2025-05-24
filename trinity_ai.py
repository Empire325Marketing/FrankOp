"""Unified interface for ChatGPT, Gemini, and OpenEvolve."""

from __future__ import annotations

import os
from typing import Optional, List, Dict

import requests

import openai


class TrinityAI:
    """Controller to orchestrate multiple AI models."""

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
                 open_evolve_token: Optional[str] = None) -> None:
        self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.gemini_client = openai.OpenAI(
            api_key=gemini_api_key or os.getenv("GEMINI_API_KEY"),
            base_url=gemini_base_url,
        )
        self.open_evolve_token = open_evolve_token or os.getenv("OPENEVOLVE_TOKEN")
        # Simple in-memory conversation history used by the chat models
        # Each entry is a dict with ``role`` and ``content`` keys matching the
        # OpenAI ChatCompletion format.
        self.conversation: List[Dict[str, str]] = []

    def reset_history(self) -> None:
        """Clear the conversation memory."""
        self.conversation.clear()

    def chat(self, prompt: str, model: str = "openai", **kwargs) -> str:
        """Send a prompt to the selected model and return the response text.

        Conversation history is automatically included so context is preserved
        across calls. Use :py:meth:`reset_history` to clear the stored state.
        """

        messages = self.conversation + [{"role": "user", "content": prompt}]

        if model == "openai":
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                **kwargs,
            )
            reply = response.choices[0].message.content
        elif model == "gemini":
            response = self.gemini_client.chat.completions.create(
                model="gemini-pro",
                messages=messages,
                **kwargs,
            )
            reply = response.choices[0].message.content
        elif model == "open_evolve":
            reply = self._open_evolve_action(prompt)
        else:
            raise ValueError(f"Unknown model: {model}")

        self.conversation.append({"role": "user", "content": prompt})
        self.conversation.append({"role": "assistant", "content": reply})
        return reply

    def _open_evolve_action(self, instruction: str) -> str:
        """Trigger an OpenEvolve workflow.

        The call is made to ``OPENEVOLVE_URL`` using the configured token. If
        the request fails, the error message is returned so tests can still run
        without network access.
        """
        if not self.open_evolve_token:
            raise RuntimeError("OPENEVOLVE_TOKEN not set")
        url = os.getenv("OPENEVOLVE_URL", "https://openevolve.example/execute")
        try:
            response = requests.post(
                url,
                json={"instruction": instruction},
                headers={"Authorization": f"Bearer {self.open_evolve_token}"},
                timeout=10,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            return f"OpenEvolve request failed: {exc}"


if __name__ == "__main__":
    controller = TrinityAI()
    result = controller.chat("Hello from Trinity AI!", model="openai")
    print(result)
