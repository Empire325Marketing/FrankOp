import unittest

from prompt_mutate import mutate_prompt, chain_mutations


class TestPromptMutate(unittest.TestCase):
    def test_mutate_prompt_replaces_known_words(self):
        self.assertEqual(mutate_prompt("hello AI"), "hi Artificial intelligence")

    def test_chain_mutations_runs_steps(self):
        history = chain_mutations("hello", steps=2)
        self.assertEqual(history, ["hello", "hi", "hi"])


if __name__ == "__main__":
    unittest.main()

