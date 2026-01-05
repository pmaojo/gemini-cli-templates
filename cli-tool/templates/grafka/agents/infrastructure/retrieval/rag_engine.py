"""RAG (Retrieval Augmented Generation) Engine"""
from typing import List, Dict, Any
from ..infrastructure.persistence.vector_store import VectorStore
from ..infrastructure.persistence.embeddings import EmbeddingGenerator
from ..infrastructure.persistence.graph_client import GraphClient

class RAGEngine:
    """Hybrid retrieval combining symbolic graph + vector search"""

    def __init__(
        self,
        ontology_service: OntologyService,
        vector_store: VectorStore,
        graph_client: GraphClient,
        embedding_generator: EmbeddingGenerator
    ):
        self.ontology = ontology_service
        self.vector_store = vector_store
        self.graph_client = graph_client
        self.embedder = embedding_generator

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Retrieve relevant context for a query"""

        # 1. Vector search
        query_vec = self.embedder.encode_single(query)
        vector_results = self.vector_store.search(query_vec, top_k=top_k)

        # 2. Graph expansion (get neighbors of top results)
        expanded_context = []
        for result in vector_results:
            # Get graph neighbors
            neighbors = self.graph_client.query_neighbors(int(result.node_id))
            expanded_context.append({
                "node": result.node_id,
                "score": result.score,
                "metadata": result.metadata,
                "neighbors": neighbors
            })

        # 3. Ontology-based filtering
        # Filter results based on ontology constraints
        filtered_results = self._filter_by_ontology(expanded_context)

        return {
            "query": query,
            "results": filtered_results,
            "context": self._format_context(filtered_results)
        }

    def _filter_by_ontology(self, results: List[Dict]) -> List[Dict]:
        """Filter results based on ontology constraints"""
        # Apply domain/range constraints, class hierarchies, etc.
        return results  # Simplified for now

    def _format_context(self, results: List[Dict]) -> str:
        """Format results as context for LLM"""
        context_parts = []
        for r in results:
            context_parts.append(f"Node {r['node']}: {r['metadata']}")
        return "\n".join(context_parts)
