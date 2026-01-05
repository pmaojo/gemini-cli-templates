"""
Pipeline Engine for Agentic Workflows
Manages the execution of multi-step semantic workflows.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
import time

@dataclass
class PipelineResult:
    success: bool
    data: Dict[str, Any]
    logs: List[str]
    execution_time: float

class PipelineStrategy(ABC):
    """Abstract base class for pipeline strategies"""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def run(self, input_data: Any, **kwargs) -> PipelineResult:
        pass

class PipelineEngine:
    """
    Registry and executor for pipelines.
    """
    def __init__(self):
        self.pipelines: Dict[str, PipelineStrategy] = {}

    def register(self, strategy: PipelineStrategy):
        self.pipelines[strategy.name] = strategy
        print(f"✓ Registered pipeline: {strategy.name}")

    def get_available_pipelines(self) -> List[str]:
        return list(self.pipelines.keys())

    def run_pipeline(self, name: str, input_data: Any, **kwargs) -> PipelineResult:
        if name not in self.pipelines:
            raise ValueError(f"Pipeline '{name}' not found")

        print(f"\n🚀 Starting Pipeline: {name}")
        start_time = time.time()

        try:
            result = self.pipelines[name].run(input_data, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return PipelineResult(
                success=False,
                data={"error": str(e)},
                logs=[f"CRITICAL ERROR: {str(e)}"],
                execution_time=time.time() - start_time
            )

        return result
