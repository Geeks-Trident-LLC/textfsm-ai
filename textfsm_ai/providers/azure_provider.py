from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from textfsm_ai.orchestrator.provider import Provider


class AzureOpenAIProvider(Provider):
    name = "azure"

    def __init__(self, endpoint: str, api_key: str):
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
        )

    def supports(self, model: str) -> bool:
        return model.startswith("azure/")

    def generate(self, prompt: str, *, model: str, temperature: float, max_tokens: int):
        deployment = model.replace("azure/", "")
        resp = self.client.complete(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {"content": resp.choices[0].message.content, "raw": resp}
