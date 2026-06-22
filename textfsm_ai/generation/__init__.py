from .controller.generation_controller import GenerationController
from .core.models import GenerationPipeline, GenerationStage


def generate(sample: str, model: str, api_key: str) -> GenerationStage:
    controller = GenerationController(api_key=api_key, model=model, max_retries=1)
    result = controller.run(sample)
    if result.last_stage is None:
        raise RuntimeError("Generation failed: no last_stage produced")
    return result.last_stage


def generate_with_corrections(
    sample: str, model: str, api_key: str, max_retries: int = 3
) -> GenerationPipeline:
    controller = GenerationController(
        api_key=api_key, model=model, max_retries=max_retries
    )
    return controller.run(sample)
