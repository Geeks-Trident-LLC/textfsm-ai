# textfsm_ai/api.py

from .ai_router import get_router


def ask_ai(prompt, provider, model, api_key, **kwargs):
    router = get_router()
    return router.send(
        prompt, provider=provider, model=model, api_key=api_key, **kwargs
    )
