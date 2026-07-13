from .model_registry import ModelRegistry


class model:
    class openai:
        class quality:
            chat = ModelRegistry.get("openai", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("openai", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("openai", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("openai", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("openai", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("openai", "thinking", "speed", "chat")

        default = ModelRegistry.alias("openai_default")

    class azure:
        class quality:
            chat = ModelRegistry.get("azure", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("azure", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("azure", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("azure", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("azure", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("azure", "thinking", "speed", "chat")

        default = ModelRegistry.alias("azure_default")

    class anthropic:
        class quality:
            chat = ModelRegistry.get("anthropic", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("anthropic", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("anthropic", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("anthropic", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("anthropic", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("anthropic", "thinking", "speed", "chat")

        default = ModelRegistry.alias("anthropic_default")

    class gemini:
        class quality:
            chat = ModelRegistry.get("gemini", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("gemini", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("gemini", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("gemini", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("gemini", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("gemini", "thinking", "speed", "chat")

        default = ModelRegistry.alias("gemini_default")

    class deepseek:
        class quality:
            chat = ModelRegistry.get("deepseek", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("deepseek", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("deepseek", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("deepseek", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("deepseek", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("deepseek", "thinking", "speed", "chat")

        default = ModelRegistry.alias("deepseek_default")

    class groq:
        class quality:
            chat = ModelRegistry.get("groq", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("groq", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("groq", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("groq", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("groq", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("groq", "thinking", "speed", "chat")

        default = ModelRegistry.alias("groq_default")

    class xai:
        class quality:
            chat = ModelRegistry.get("xai", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("xai", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("xai", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("xai", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("xai", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("xai", "thinking", "speed", "chat")

        default = ModelRegistry.alias("xai_default")

    class together:
        class quality:
            chat = ModelRegistry.get("together", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("together", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("together", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("together", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("together", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("together", "thinking", "speed", "chat")

        default = ModelRegistry.alias("together_default")

    class fireworks:
        class quality:
            chat = ModelRegistry.get("fireworks", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("fireworks", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("fireworks", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("fireworks", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("fireworks", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("fireworks", "thinking", "speed", "chat")

        default = ModelRegistry.alias("fireworks_default")

    class cerebras:
        class quality:
            chat = ModelRegistry.get("cerebras", "quality", "chat")

        class balance:
            chat = ModelRegistry.get("cerebras", "balance", "chat")

        class speed:
            chat = ModelRegistry.get("cerebras", "speed", "chat")

        class thinking:
            class quality:
                chat = ModelRegistry.get("cerebras", "thinking", "quality", "chat")

            class balance:
                chat = ModelRegistry.get("cerebras", "thinking", "balance", "chat")

            class speed:
                chat = ModelRegistry.get("cerebras", "thinking", "speed", "chat")

        default = ModelRegistry.alias("cerebras_default")
