from .anthropic_provider import AnthropicProvider
from .azure_provider import AzureOpenAIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .registry import registry

registry.register(OpenAIProvider)
registry.register(AnthropicProvider)
registry.register(GeminiProvider)
registry.register(AzureOpenAIProvider)
