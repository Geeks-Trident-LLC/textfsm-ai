# textfsm_ai/delivery/controller/controller.py

import time

from textfsm_ai.delivery.core.modes import DeliveryMode
from textfsm_ai.delivery.engine.engine import DeliveryEngine
from textfsm_ai.dsl.controller.dsl_controller import DSLController
from textfsm_ai.generation.controller.generation_controller import GenerationController


class DeliveryController:
    def __init__(self, api_key: str, model: str):
        self._gen = GenerationController(api_key=api_key, model=model)
        self._dsl = DSLController()
        self._engine = DeliveryEngine(model=model)

    def run(self, sample: str, mode: str):
        mode_enum = DeliveryMode.from_str(mode)

        start = time.perf_counter()

        # 1. Generation
        gen = self._gen.run(sample)

        # 2. DSL
        canonical = self._dsl.canonicalize(gen)
        machine = self._dsl.to_machine_dsl(canonical)
        human = self._dsl.to_human_dsl(machine, sample)
        recognizer = self._dsl.recognize(machine, sample)
        duration_ms = int((time.perf_counter() - start) * 1000)

        # 3. Delivery engine
        return self._engine.assemble(
            mode=mode_enum,
            generation=gen,
            canonical=canonical,
            machine_dsl=machine,
            human_dsl=human,
            recognizer=recognizer,
            duration_ms=duration_ms,
        )
