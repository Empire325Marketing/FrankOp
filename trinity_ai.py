"""Unified interface for ChatGPT, Gemini, and OpenEvolve.

TODO: integrate with the actual OpenEvolve backend once it becomes
available. Currently the OpenEvolve support merely dispatches a placeholder
GitHub workflow.
"""

from __future__ import annotations

import os
from typing import Optional

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

    def chat(self, prompt: str, model: str = "openai", **kwargs) -> str:
        """Send a prompt to the selected model and return the response text."""
        if model == "openai":
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content
        if model == "gemini":
            response = self.gemini_client.chat.completions.create(
                model="gemini-pro",
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content
        if model == "open_evolve":
            return self._open_evolve_action(prompt)
        raise ValueError(f"Unknown model: {model}")

    def _open_evolve_action(self, instruction: str) -> str:
        """Trigger an OpenEvolve GitHub workflow.

        TODO: replace this placeholder implementation with calls to the
        official OpenEvolve API once it is released.
        """

        if not self.open_evolve_token:
            raise RuntimeError("OPENEVOLVE_TOKEN environment variable not set")

        repo = os.getenv("OPENEVOLVE_REPO", "Empire325Marketing/FrankOp")
        workflow = os.getenv("OPENEVOLVE_WORKFLOW", "deploy.yml")
        url = (
            "https://api.github.com/repos/"
            f"{repo}/actions/workflows/{workflow}/dispatches"
        )

        headers = {
            "Authorization": f"Bearer {self.open_evolve_token}",
            "Accept": "application/vnd.github+json",
        }

        payload = {"ref": "main", "inputs": {"instruction": instruction}}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:
            return f"[OpenEvolve error] {exc}"

        return "[OpenEvolve workflow dispatched]"


if __name__ == "__main__":
    controller = TrinityAI()
    result = controller.chat("Hello from Trinity AI!", model="openai")
    print(result)
