from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

@dataclass(frozen=True)
class Triple:
    subject: str
    predicate: str
    object: str

    def __post_init__(self):
        if not self.subject:
            raise ValueError("Subject cannot be empty")
        if not self.predicate:
            raise ValueError("Predicate cannot be empty")
        if not self.object:
            raise ValueError("Object cannot be empty")

    def to_tuple(self):
        return (self.subject, self.predicate, self.object)

@dataclass
class InferenceResult:
    original_triples: List[Triple]
    inferred_triples: List[Triple]
    expansion_ratio: float
    rules_applied: Dict[str, int]
    execution_time: float = 0.0

    @property
    def total_triples(self):
        return len(self.original_triples) + len(self.inferred_triples)
