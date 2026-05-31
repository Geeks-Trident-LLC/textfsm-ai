import requests

from textfsm_ai.quota_manager import QuotaManager


class GeminiProvider:
    def __init__(self, api_key, model, daily_limit, monthly_limit):
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.quota = QuotaManager("gemini", daily_limit, monthly_limit)

    def generate(self, prompt: str) -> str:
        estimated_tokens = len(prompt.split()) * 2
        if not self.quota.allowed(estimated_tokens):
            raise RuntimeError("Gemini quota exceeded")

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}

        resp = requests.post(self.url, json=payload, params=params, timeout=30)
        resp.raise_for_status()

        self.quota.add_tokens(estimated_tokens)
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
