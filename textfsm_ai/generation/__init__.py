from .controller.generation_controller import GenerationController
from .core.models import GenerationPipeline, GenerationStage


def generate(
    provider_name: str, model: str, api_key: str, sample: str, max_retries=1
) -> GenerationStage:
    controller = GenerationController(
        provider_name=provider_name,
        api_key=api_key,
        model=model,
        max_retries=max_retries,
    )
    result = controller.run(sample)
    if result.last_stage is None:
        raise RuntimeError("Generation failed: no last_stage produced")
    return result.last_stage


def generate_with_corrections(
    provider_name: str, model: str, api_key: str, sample: str, max_retries: int = 3
) -> GenerationPipeline:
    controller = GenerationController(
        provider_name=provider_name,
        api_key=api_key,
        model=model,
        max_retries=max_retries,
    )
    return controller.run(sample)
