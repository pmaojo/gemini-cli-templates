from typing import List, Any
from agents.domain.entities import Triple, InferenceResult
from agents.domain.ports import IGraphRepository

class ReasonWithOWLUseCase:
    def __init__(self, reasoner_agent: Any = None, graph_repo: IGraphRepository = None, reasoning_engine: Any = None):
        # Support both names for compatibility
        self.reasoner = reasoner_agent or reasoning_engine
        self.graph_repo = graph_repo

    def execute(self, triples: List[Triple], tenant_id: str = "default", auto_store: bool = True) -> InferenceResult:
        # Convert domain triples to tuples for reasoning agent
        input_tuples = [(t.subject, t.predicate, t.object) for t in triples]

        # Reason
        if self.reasoner:
            result = self.reasoner.infer(input_tuples)
        else:
             result = {"inferred_triples": [], "rules_applied": {}}

        # Convert back
        inferred_triples = [
            Triple(s, p, o)
            for s, p, o in result.get('inferred_triples', [])
        ]

        # Store
        if auto_store and inferred_triples and self.graph_repo:
            self.graph_repo.ingest_triples(inferred_triples, tenant_id)

        return InferenceResult(
            original_triples=triples,
            inferred_triples=inferred_triples,
            expansion_ratio=len(inferred_triples) / len(triples) if triples else 0.0,
            rules_applied=result.get('rules_applied', {}),
            execution_time=0.0 # Placeholder
        )
