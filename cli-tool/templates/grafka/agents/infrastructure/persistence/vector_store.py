"""Vector store interface using Qdrant"""
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

@dataclass
class VectorSearchResult:
    node_id: str
    score: float
    metadata: Dict[str, Any]

class VectorStore:
    """Vector store implementation using Qdrant"""

    def __init__(self, collection_name: str = "semantic_graph", dimension: int = 384, url: str = None, client: Optional[QdrantClient] = None, tenant_id: str = None):
        self.base_collection_name = collection_name
        self.dimension = dimension
        self.tenant_id = tenant_id

        if client:
            self.client = client
        elif url:
            self.client = QdrantClient(url=url)
        else:
            # Check env var or fallback to local disk persistence
            env_url = os.getenv("QDRANT_URL")
            if env_url:
                self.client = QdrantClient(url=env_url)
            else:
                # Local persistence in ./qdrant_storage
                storage_path = os.path.join(os.getcwd(), "qdrant_storage")
                os.makedirs(storage_path, exist_ok=True)
                print(f"Initializing local Qdrant storage at {storage_path}")
                self.client = QdrantClient(path=storage_path)

        self._ensure_collection(self.get_collection_name())

    def get_collection_name(self, tenant_id: Optional[str] = None) -> str:
        if tenant_id:
            return f"{self.base_collection_name}_{tenant_id}"
        if self.tenant_id:
            return f"{self.base_collection_name}_{self.tenant_id}"
        return self.base_collection_name

    def _ensure_collection(self, collection_name: str):
        collections = self.client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.dimension,
                    distance=models.Distance.COSINE
                )
            )

    def add(self, node_id: str, vector: np.ndarray, metadata: Optional[Dict] = None, tenant_id: Optional[str] = None):
        if vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: {vector.shape[0]} != {self.dimension}")

        collection = self.get_collection_name(tenant_id)
        self._ensure_collection(collection)

        import uuid
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, node_id))

        self.client.upsert(
            collection_name=collection,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload={
                        "original_id": node_id,
                        **(metadata or {})
                    }
                )
            ]
        )

    def search(self, query_vector: np.ndarray, top_k: int = 10, tenant_id: Optional[str] = None) -> List[VectorSearchResult]:
        collection = self.get_collection_name(tenant_id)
        try:
            results = self.client.query_points(
                collection_name=collection,
                query=query_vector.tolist(),
                limit=top_k
            )

            return [
                VectorSearchResult(
                    node_id=hit.payload.get("original_id", str(hit.id)),
                    score=hit.score,
                    metadata=hit.payload
                )
                for hit in results.points
            ]
        except Exception as e:
            if "Not found" in str(e):
                return []
            raise e

    def delete(self, node_id: str, tenant_id: Optional[str] = None):
        import uuid
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, node_id))
        collection = self.get_collection_name(tenant_id)
        self.client.delete(
            collection_name=collection,
            points_selector=models.PointIdsList(
                points=[point_id]
            )
        )
