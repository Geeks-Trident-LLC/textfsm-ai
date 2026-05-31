import requests

from textfsm_ai.quota_manager import QuotaManager


class OpenAIProvider:
    def __init__(self, api_key, model, daily_limit, monthly_limit):
        self.api_key = api_key
        self.model = model
        self.url = "https://api.openai.com/v1/chat/completions"
        self.quota = QuotaManager("openai", daily_limit, monthly_limit)

    def generate(self, prompt: str) -> str:
        estimated_tokens = len(prompt.split()) * 2
        if not self.quota.allowed(estimated_tokens):
            raise RuntimeError("OpenAI quota exceeded")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }

        resp = requests.post(self.url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()

        self.quota.add_tokens(estimated_tokens)
        return resp.json()["choices"][0]["message"]["content"]
