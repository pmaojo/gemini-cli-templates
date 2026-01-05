from abc import ABC, abstractmethod
from typing import List, Optional, Any
from agents.domain.entities import Triple

class IGraphRepository(ABC):
    @abstractmethod
    def ingest_triples(self, triples: List[Triple], tenant_id: str) -> bool:
        pass

    @abstractmethod
    def get_all_triples(self, tenant_id: str) -> List[Triple]:
        pass

class IEmbeddingService(ABC):
    @abstractmethod
    def encode_single(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        pass
