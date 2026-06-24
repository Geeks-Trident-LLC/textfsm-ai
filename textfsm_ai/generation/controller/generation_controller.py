# textfsm_ai/generation/controller/generation_controller.py

from textfsm_ai.generation.core.models import GenerationPipeline, GenerationStage
from textfsm_ai.generation.engine import (
    generation_engine as engine,
)


class GenerationController:
    """Stateless orchestrator for generation pipeline."""

    def __init__(
        self,
        provider_name: str,
        api_key: str,
        model: str,
        endpoint: str = "",
        api_version: str = "",
        max_retries: int = 1,
    ):
        self.provider_name = provider_name
        self.api_key = api_key
        self.model = model
        self.max_retries = max_retries
        self.endpoint = endpoint
        self.api_version = api_version

    def run(self, sample: str, **kwargs) -> GenerationPipeline:

        stages = []
        last_result = GenerationStage("", [])

        retryable_errors = []

        # ------------------------------------------------------------
        # 1. Base generation phase
        # ------------------------------------------------------------
        for attempt in range(self.max_retries):
            result = engine.run(
                provider_name=self.provider_name,
                api_key=self.api_key,
                model=self.model,
                sample=sample,
                endpoint=self.endpoint,
                api_version=self.api_version,
                **kwargs,
            )
            last_result = result
            stages.append(result)

            if result.ready:
                result.name = "generate-using-base-prompt"
                return GenerationPipeline(
                    model=self.model,
                    stages=stages,
                    last_stage=result,
                    sample=sample,
                    attempts=attempt + 1,
                    max_retries=self.max_retries,
                    ready=True,
                )

            if is_unretryable_error(result.reason):
                result.name = "generate-using-base-prompt-with-error-not-retryable"
                return GenerationPipeline(
                    model=self.model,
                    stages=stages,
                    last_stage=result,
                    sample=sample,
                    attempts=attempt + 1,
                    max_retries=self.max_retries,
                    reason=result.reason,
                    ready=False,
                )

            retryable_errors.append(is_retryable_error(result.reason))

            result.name = f"generate-using-base-prompt-retry-#{attempt + 1}"

        # Base generation never succeeded structurally
        if all(retryable_errors):
            last_result.name = "generate-base-all-retries-exhausted"
            return GenerationPipeline(
                model=self.model,
                stages=stages,
                last_stage=last_result,
                sample=sample,
                attempts=self.max_retries,
                max_retries=self.max_retries,
                ready=False,
                reason=last_result.reason,
            )

        # ------------------------------------------------------------
        # 2. Correction prompt phase
        # ------------------------------------------------------------
        for attempt in range(self.max_retries):
            result = engine.run_correction_prompt(
                provider_name=self.provider_name,
                api_key=self.api_key,
                model=self.model,
                sample=sample,
                prev_result=last_result,
                endpoint=self.endpoint,
                api_version=self.api_version,
                **kwargs,
            )
            last_result = result
            stages.append(result)

            if result.ready:
                result.name = "generate-using-correction-prompt"
                return GenerationPipeline(
                    model=self.model,
                    stages=stages,
                    last_stage=result,
                    sample=sample,
                    attempts=attempt + 1,
                    max_retries=self.max_retries,
                    ready=True,
                )

            result.name = f"generate-using-correction-prompt-retry-#{attempt + 1}"

        # ------------------------------------------------------------
        # 3. Correction attempts exhausted
        # ------------------------------------------------------------
        last_result.name = "generate-correction-all-retries-exhausted"
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


def is_unretryable_error(reason: str) -> bool:
    """
    Return True if the LLM error is fatal and should NOT be retried.
    Expected format: 'LLM-ERROR-{err_type}-{err_msg}'.
    """

    if not reason or not reason.startswith("LLM-ERROR-"):
        # No reason or not an LLM error → treat as NOT fatal
        return False

    # Extract the error type: LLM-ERROR-{type}-{msg}
    parts = reason.split("-", maxsplit=3)
    if len(parts) < 3:
        return False

    err_type = parts[2].lower()

    unretryable = {
        "invalid_argument",
        "bad_request",
        "unsupported_model",
        "authentication_error",
        "permission_denied",
        "content_filtered",
        "safety_blocked",
    }

    return err_type in unretryable


def is_retryable_error(reason: str) -> bool:
    """
    Return True if the LLM error is transient and should be retried.
    Expected format: 'LLM-ERROR-{err_type}-{err_msg}'.
    """

    if not reason or not reason.startswith("LLM-ERROR-"):
        return False

    # Extract the error type: LLM-ERROR-{type}-{msg}
    parts = reason.split("-", maxsplit=3)
    if len(parts) < 3:
        return False

    err_type = parts[2].lower()

    retryable = {
        "unavailable",
        "resource_exhausted",
        "rate_limit",
        "overloaded",
        "backend_error",
        "timeout",
        "cancelled",
        "deadline_exceeded",
    }

    return err_type in retryable
