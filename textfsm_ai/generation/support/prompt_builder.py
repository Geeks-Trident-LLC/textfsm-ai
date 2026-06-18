# textfsm_ai/generation/support/prompt_builder.py

from pathlib import Path

import yaml

from textfsm_ai import BASE_DIR

PROMPTS_PATH = BASE_DIR / "generation" / "core" / "prompts.yaml"


class PromptBuilder:
    def __init__(self, prompts_path: Path = PROMPTS_PATH):
        self.prompts_path = prompts_path
        self.prompts = self._load_yaml(prompts_path)

    def _load_yaml(self, path: Path) -> dict:
        """Load and return YAML content as a dictionary."""
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return yaml.safe_load(path.read_text())

    def _get(self, key: str) -> str:
        """Retrieve a prompt template by key."""
        try:
            return self.prompts[key]
        except KeyError:
            raise KeyError(f"Prompt '{key}' not found in {self.prompts_path}")

    def base_prompt(self, sample: str) -> str:
        base = self._get("base")
        return f"{base}\n\nSample\n=============================\n{sample}"

    def correction_prompt(self, sample: str, prev_response: str, finding: list) -> str:
        correction_prompt = self._get("correction").format(
            base=self._get("base"),
            prev_response=prev_response,
            finding=finding,
            sample=sample,
        )

        return correction_prompt
