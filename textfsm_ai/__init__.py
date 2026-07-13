# textfsm_ai/__init__.py

from pathlib import Path

__version__ = "0.4.1"
version = __version__

BASE_DIR: Path = Path(__file__).resolve().parent

from .api import (  # noqa: E402
    DSLResult,
    LLMResult,
    compile_dsl,
    generate,
    parse_to_dicts,
    parse_to_lists,
    run_pipeline,
    to_ast,
    to_canonical,
    to_dsl_result,
    to_llm_handling,
    to_llm_records,
    to_llm_result,
    to_llm_template,
    to_llm_variables,
    to_readable,
    to_recognizers,
    validate_template,
)

__all__ = [
    "BASE_DIR",
    "version",
    "__version__",
    "LLMResult",
    "DSLResult",
    "generate",
    "to_llm_result",
    "to_llm_template",
    "to_llm_records",
    "to_llm_variables",
    "to_llm_handling",
    "compile_dsl",
    "to_dsl_result",
    "to_ast",
    "to_canonical",
    "to_readable",
    "to_recognizers",
    "parse_to_dicts",
    "parse_to_lists",
    "validate_template",
    "run_pipeline",
]
