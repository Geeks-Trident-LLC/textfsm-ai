from typing import Optional


def list_models(provider: str, api_key: Optional[str] = None) -> list[str]:
    """
    Unified model listing across OpenAI, DeepSeek, Anthropic, and Gemini.
    Returns a list of model IDs/names. Returns [] on failure.
    """
    provider = provider.lower()

    try:
        if provider == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            return [m.id for m in client.models.list().data]

        if provider == "deepseek":
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            return [m.id for m in client.models.list().data]

        if provider == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            return [m.id for m in client.models.list().data]

        if provider == "gemini":
            from google import genai

            client = genai.Client(api_key=api_key)
            return [m.name for m in client.models.list()]

    except Exception:
        return []

    return []


def get_model(
    provider: str, api_key: Optional[str] = None, model_tier: str = "reg"
) -> str:
    provider = provider.lower()
    model_tier = model_tier.lower()

    lst = list_models(provider, api_key)
    if not lst:
        raise ValueError(f"No models found for provider '{provider}'")

    # Normalize Gemini "models/xxx"
    lst = [m.split("/")[-1] for m in lst]

    # Keep only NLP models
    lst = [m for m in lst if is_chat_model(provider, m)]
    if not lst:
        raise ValueError(f"No NLP models found for provider '{provider}'")

    # Sort newest → oldest
    lst = sorted(lst, reverse=True)

    # Pick classifier
    if provider == "openai":
        classify = classify_openai
    elif provider == "deepseek":
        classify = classify_deepseek
    elif provider == "anthropic":
        classify = classify_anthropic
    elif provider == "gemini":
        classify = classify_gemini
    else:
        raise ValueError(f"Unknown provider '{provider}'")

    # Bucket models
    pro = [m for m in lst if classify(m) == "pro"]
    reg = [m for m in lst if classify(m) == "reg"]
    eco = [m for m in lst if classify(m) == "eco"]

    # Select tier
    if model_tier == "pro":
        return pro[0] if pro else (reg[0] if reg else eco[0])

    if model_tier == "reg":
        return reg[0] if reg else (pro[0] if pro else eco[0])

    if model_tier == "eco":
        return eco[0] if eco else (reg[0] if reg else pro[0])

    raise ValueError(f"Unknown model tier '{model_tier}'")


def classify_anthropic(m: str) -> str:
    m = m.lower()
    if "opus" in m:
        return "pro"
    if "sonnet" in m:
        return "reg"
    if "haiku" in m:
        return "eco"
    return "reg"


def classify_openai(m: str) -> str:
    m = m.lower()

    # PRO tier
    if any(x in m for x in ["gpt-5", "gpt-4.1", "gpt-4o"]) and "mini" not in m:
        return "pro"

    # ECO tier
    if "mini" in m:
        return "eco"

    # REG tier
    return "reg"


def classify_deepseek(m: str) -> str:
    m = m.lower()
    if "flash" in m:
        return "reg"
    if "chat" in m:
        return "eco"
    return "pro"


def classify_gemini(m: str) -> str:
    m = m.lower()

    if "pro" in m:
        return "pro"
    if "flash" in m and "lite" not in m:
        return "reg"
    if "lite" in m or "gemma" in m:
        return "eco"

    return "reg"


def is_chat_model(provider: str, name: str) -> bool:
    n = name.lower()

    # Reject known non-chat categories
    BAD = [
        "embed",
        "embedding",
        "audio",
        "whisper",
        "tts",
        "asr",
        "image",
        "vision",
        "clip",
        "veo",
        "imagen",
        "realtime",
        "translate",
        "preview",
        "experimental",
    ]
    if any(b in n for b in BAD):
        return False

    # Provider-specific chat keywords
    if provider == "openai":
        return n.startswith("gpt")
    if provider == "anthropic":
        return n.startswith("claude")
    if provider == "gemini":
        return n.startswith("gemini")
    if provider == "deepseek":
        return n.startswith("deepseek")

    return False
