"""Simple simulator that applies prompt mutations in a loop."""

from __future__ import annotations

import time
from typing import Iterable

from prompt_mutate import chain_mutations, mutate_prompt


def simulate(prompt: str, cycles: int = 3, delay: float = 0.0) -> list[str]:
    """Run *prompt* through several mutation cycles.

    Parameters
    ----------
    prompt:
        Initial prompt text.
    cycles:
        How many mutation steps to apply.
    delay:
        Optional sleep between cycles to emulate processing delay.
    """
    history = [prompt]
    current = prompt
    for _ in range(cycles):
        current = mutate_prompt(current)
        history.append(current)
        if delay:
            time.sleep(delay)
    return history


if __name__ == "__main__":  # pragma: no cover - CLI helper
    import argparse

    parser = argparse.ArgumentParser(description="Run a prompt mutation simulation")
    parser.add_argument("prompt")
    parser.add_argument("--cycles", type=int, default=3, help="Number of mutation cycles")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between cycles in seconds")
    args = parser.parse_args()

    for idx, text in enumerate(simulate(args.prompt, args.cycles, args.delay)):
        print(f"[{idx}] {text}")

