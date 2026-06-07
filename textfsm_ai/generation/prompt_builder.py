from pathlib import Path

import yaml

PROMPTS_PATH = Path(__file__).parent / "prompts.yaml"


class PromptBuilder:
    """
    Loads prompt templates from prompts.yaml and formats them with runtime values.

    Expected YAML keys:
      - one_pass_prompt
      - two_pass_prompt_a
      - two_pass_prompt_b
    """

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

    def one_pass_prompt(self, sample: str) -> str:
        """
        Returns the one-pass prompt with the sample appended safely.
        """
        base = self._get("one_pass_prompt")
        return f"{base}\n{sample}"

    def two_pass_prompt_a(self, sample: str) -> str:
        """
        Returns the first-pass prompt with the sample appended safely.
        """
        base = self._get("two_pass_prompt_a")
        return f"{base}\n{sample}"

    def two_pass_prompt_b(self, sections_text: str) -> str:
        """
        Returns the second-pass prompt with the four-section text appended safely.
        """
        base = self._get("two_pass_prompt_b")
        return f"{base}\n{sections_text}"
