# textfsm_ai/generation/engine/extractor.py

from dataclasses import dataclass
from typing import Optional

from textfsm_ai.core.serializable import Serializable


@dataclass
class LLMRunResult(Serializable):
    provider: str
    model: str
    sample: str
    prompt: str
    response: str
    next_prompt: Optional[str] = None
    next_response: Optional[str] = None

    def to_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "sample": self.sample,
            "prompt": self.prompt,
            "response": self.response,
            "next_prompt": self.next_prompt,
            "next_response": self.next_response,
        }


def extract(provider_name: str, model: str, sample: str, prompt: str, response: str):
    return LLMRunResult(
        provider=provider_name,
        model=model,
        sample=sample,
        prompt=prompt,
        response=response,
    )


def next_extract(llm_run_result, prompt: str, response: str):
    llm_run_result.next_prompt = prompt
    llm_run_result.next_response = response
