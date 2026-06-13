# textfsm_ai/generation/engine/one_pass.py

from textfsm_ai.generation.support import prompt_builder
from textfsm_ai.providers.registry import get_provider_for_model

from ..support import extractor, llm_extractor


def run(api_key: str, model: str, sample: str):
    provider = get_provider_for_model(model)(api_key, model)
    prompt = prompt_builder.PromptBuilder().one_pass_prompt(sample)
    response = llm_extractor.extract(provider, model, prompt)
    llm_run_result = extractor.extract(provider.name, model, sample, prompt, response)
    return llm_run_result
