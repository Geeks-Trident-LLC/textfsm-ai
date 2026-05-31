import requests

from textfsm_ai.quota_manager import QuotaManager


class ClaudeProvider:
    def __init__(self, api_key, model, daily_limit, monthly_limit):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.anthropic.com/v1/messages"
        self.quota = QuotaManager("claude", daily_limit, monthly_limit)

    def generate(self, prompt: str) -> str:
        estimated_tokens = len(prompt.split()) * 2
        if not self.quota.allowed(estimated_tokens):
            raise RuntimeError("Claude quota exceeded")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }

        resp = requests.post(self.url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()

        self.quota.add_tokens(estimated_tokens)
        return resp.json()["content"][0]["text"]
