# textfsm_ai/generation/llm_extractor.py


def extract(provider, model: str, prompt: str) -> str:
    response = provider.generate_sync(prompt, model=model).get("content", "")
    return response or ""
