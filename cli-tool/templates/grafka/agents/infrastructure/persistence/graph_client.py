"""Client to interact with the Rust graph engine via gRPC"""
import grpc
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphClient:
    """Client for the semantic graph engine"""

    def __init__(self, host: str = "localhost", port: int = 50051):
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None

    def connect(self):
        """Establish connection to the graph engine"""
        try:
            self.channel = grpc.insecure_channel(self.address)
            # Try to import generated stubs
            try:
                from . import semantic_engine_pb2, semantic_engine_pb2_grpc
                self.stub = semantic_engine_pb2_grpc.SemanticEngineStub(self.channel)
                logger.info(f"Connected to graph engine at {self.address} with gRPC stubs")
            except ImportError:
                logger.warning(f"Connected to {self.address} but stubs not found. Run setup.sh.")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")

    def ingest_triples(self, triples: List[List[str]]) -> Dict[str, int]:
        """Send triples to the graph engine"""
        if not self.stub:
            logger.warning("Stubs not loaded, returning mock response for ingestion")
            return {"nodes_added": len(triples), "edges_added": len(triples)}

        try:
            from . import semantic_engine_pb2
            request = semantic_engine_pb2.IngestRequest(
                triples=[semantic_engine_pb2.Triple(subject=s, predicate=p, object=o) for s, p, o in triples],
                tenant_id="default"
            )
            response = self.stub.IngestTriples(request)
            return {"nodes_added": response.nodes_added, "edges_added": response.edges_added}
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return {"error": str(e)}

    def query_neighbors(self, node_id: int) -> List[Dict[str, Any]]:
        """Query neighbors of a node"""
        if not self.stub:
            return []

        try:
            from . import semantic_engine_pb2
            request = semantic_engine_pb2.NodeRequest(node_id=node_id, tenant_id="default")
            response = self.stub.GetNeighbors(request)
            return [{"node_id": n.node_id, "edge_type": n.edge_type} for n in response.neighbors]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def close(self):
        """Close the connection"""
        if self.channel:
            self.channel.close()
