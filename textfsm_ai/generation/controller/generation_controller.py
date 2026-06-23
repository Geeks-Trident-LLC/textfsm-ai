# textfsm_ai/generation/controller/generation_controller.py

from textfsm_ai.generation.core.models import GenerationPipeline
from textfsm_ai.generation.engine import (
    generation_engine as engine,
)


class GenerationController:
    """Stateless orchestrator for generation pipeline."""

    def __init__(
        self, provider_name: str, api_key: str, model: str, max_retries: int = 1
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries

    def run(self, sample: str) -> GenerationPipeline:

        stages = []
        last_result = None

        for attempt in range(self.max_retries):
            # ----------------------------------------
            # Attempt 0 → base generation
            # ----------------------------------------
            if attempt == 0:
                result = engine.run(
                    provider_name=self.provider_name,
                    api_key=self.api_key,
                    model=self.model,
                    sample=sample,
                )
                last_result = result
                stages.append(result)

                if result.ready:
                    return GenerationPipeline(
                        model=self.model,
                        stages=stages,
                        last_stage=result,
                        sample=sample,
                        attempts=attempt + 1,
                        max_retries=self.max_retries,
                        ready=True,
                    )

                continue

            # ----------------------------------------
            # Attempt > 0 → correction prompt
            # ----------------------------------------
            assert last_result is not None
            result = engine.run_correction_prompt(
                provider_name=self.provider_name,
                api_key=self.api_key,
                model=self.model,
                sample=sample,
                prev_result=last_result,
            )
            result.name = "generate-using-correction-prompt"
            last_result = result
            stages.append(result)

            if result.ready:
                return GenerationPipeline(
                    model=self.model,
                    stages=stages,
                    last_stage=result,
                    sample=sample,
                    attempts=attempt + 1,
                    max_retries=self.max_retries,
                    ready=True,
                )

        # ----------------------------------------
        # All attempts exhausted
        # ----------------------------------------
        return GenerationPipeline(
            model=self.model,
            stages=stages,
            last_stage=last_result,
            sample=sample,
            attempts=self.max_retries,
            max_retries=self.max_retries,
            reason=last_result.reason if last_result else "",
            ready=last_result.ready if last_result else False,
        )
