from .controller.generation_controller import GenerationController
from .core.models import GenerationControllerResult, GenerationResult


def generate(sample: str, model: str, api_key: str) -> GenerationResult:
    controller = GenerationController(api_key=api_key, model=model, max_retries=1)
    result = controller.run(sample)
    return result.last_stage


def generate_with_corrections(
    sample: str, model: str, api_key: str, max_retries: int = 3
) -> GenerationControllerResult:
    controller = GenerationController(
        api_key=api_key, model=model, max_retries=max_retries
    )
    return controller.run(sample)
