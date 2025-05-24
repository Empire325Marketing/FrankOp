"""Utility functions for mutating chat prompts."""

from __future__ import annotations

import random
from typing import Iterable


_REPLACEMENTS = {
    "hello": "hi",
    "goodbye": "farewell",
    "ai": "artificial intelligence",
}


def mutate_prompt(prompt: str) -> str:
    """Return a slightly modified version of *prompt*.

    The mutation is intentionally simple and deterministic so it can be used
    in tests or simulations without unpredictable output.
    """
    words = []
    for word in prompt.split():
        key = word.lower()
        replacement = _REPLACEMENTS.get(key)
        if replacement:
            # Preserve original casing if the word was capitalised
            if word[0].isupper():
                replacement = replacement.capitalize()
            words.append(replacement)
        else:
            words.append(word)
    return " ".join(words)


def chain_mutations(prompt: str, steps: int = 3) -> list[str]:
    """Apply :func:`mutate_prompt` repeatedly and return all intermediate prompts."""
    history = [prompt]
    current = prompt
    for _ in range(steps):
        current = mutate_prompt(current)
        history.append(current)
    return history


if __name__ == "__main__":  # pragma: no cover - simple CLI helper
    import argparse

    parser = argparse.ArgumentParser(description="Mutate a prompt")
    parser.add_argument("prompt")
    parser.add_argument("--steps", type=int, default=1, help="Number of mutations to apply")
    args = parser.parse_args()

    history = chain_mutations(args.prompt, args.steps)
    for idx, text in enumerate(history):
        print(f"[{idx}] {text}")

