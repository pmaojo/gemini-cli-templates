"""
Dependency Injection Container
Manages singleton instances of core services.
"""
from typing import Optional, Any

class DIContainer:
    _instance = None

    def __init__(self):
        self._services = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DIContainer()
        return cls._instance

    def graph_repository(self):
        # Return Rust client wrapper
        from agents.infrastructure.web.client import get_client
        return get_client()

    def embedding_service(self):
        from agents.infrastructure.persistence.embeddings import EmbeddingGenerator
        if "embedding_service" not in self._services:
            self._services["embedding_service"] = EmbeddingGenerator()
        return self._services["embedding_service"]

    def vector_store(self, collection_name: str):
        import os
        from agents.infrastructure.persistence.vector_store import VectorStore
        from qdrant_client import QdrantClient

        if "qdrant_client" not in self._services:
             qdrant_url = os.getenv("QDRANT_URL")
             if qdrant_url:
                 # Connect to Qdrant server
                 self._services["qdrant_client"] = QdrantClient(url=qdrant_url)
             else:
                 # Fallback to local storage
                 self._services["qdrant_client"] = QdrantClient(path="./qdrant_storage")

        return VectorStore(
            collection_name=collection_name,
            dimension=384,
            client=self._services["qdrant_client"]
        )

    def ontology_service(self):
        from agents.domain.services.ontology import OntologyService
        if "ontology_service" not in self._services:
            # Load default ontologies
            self._services["ontology_service"] = OntologyService(["ontology/core.owl", "ontology/agriculture.owl"])
        return self._services["ontology_service"]

    def reasoning_engine(self):
        from agents.tools.owl_reasoner import OWLReasoningAgent
        ontology = self.ontology_service()
        return OWLReasoningAgent(ontology.graph)

def get_container():
    return DIContainer.get_instance()
