# textfsm_ai/delivery/controller/controller.py

import time

from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.engine.engine import DeliveryEngine
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController


class DeliveryController:
    def __init__(
        self,
        provider_name: str,
        api_key: str,
        model: str,
        endpoint: str = "",
        api_version: str = "",
        region: str = "",
        project: str = "",
        max_tries: int = 1,
    ):
        self._model_info = dict(
            provider_name=provider_name,
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            api_version=api_version,
            region=region,
            project=project,
        )

        self._gen = GenerationController(
            provider_name=provider_name,
            api_key=api_key,
            model=model,
            endpoint=endpoint,
            api_version=api_version,
            region=region,
            project=project,
            max_retries=max_tries,
        )
        self._dsl = DSLController()
        self._engine = DeliveryEngine()

    def run(self, sample: str, mode: str, as_json=False):
        mode_enum = DeliveryMode.from_str(mode)

        start = time.perf_counter()

        # 1. Generation
        gen_pipeline = self._gen.run(sample)

        # 2. DSL
        dsl_pipeline = self._dsl.run(gen_pipeline)
        duration_ms = int((time.perf_counter() - start) * 1000)

        # 3. Delivery engine
        return self._engine.assemble(
            mode=mode_enum,
            model_info=self._model_info,
            generation_pipeline=gen_pipeline,
            dsl_pipeline=dsl_pipeline,
            duration_ms=duration_ms,
            as_json=as_json,
        )
