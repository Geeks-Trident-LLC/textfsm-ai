# textfsm_ai/generation/engine/extractor.py


from textfsm_ai.generation.core.models import LLMRunResult


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
