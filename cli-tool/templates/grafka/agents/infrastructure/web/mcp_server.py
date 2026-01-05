"""MCP (Model Context Protocol) Server Implementation"""
import json
import asyncio
import os
import sys
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Ensure we can import modules
sys.path.append(os.getcwd())

# Local imports
try:
    from agents.infrastructure.persistence.graph_client import GraphClient
    from agents.infrastructure.persistence.vector_store import VectorStore
    from agents.infrastructure.persistence.embeddings import EmbeddingGenerator
    from agents.application.orchestration.llm_manager import LLMPipelineManager
    from agents.domain.services.ontology import OntologyService
    from agents.application.pipelines.datasyn import DataSynPipeline
except ImportError:
    # Graceful degradation for setup time or missing deps
    GraphClient = None
    VectorStore = None
    EmbeddingGenerator = None
    LLMPipelineManager = None
    OntologyService = None
    DataSynPipeline = None

# Define the server
mcp = FastMCP("Grafka Neuro-Symbolic Engine")

class ServerContext:
    def __init__(self):
        self.graph_client = None
        self.vector_store = None
        self.embedder = None
        self.pipeline_manager = None
        self.pipeline_engine = None
        self.ontology_graph = None # The actual RDFLib graph

context = ServerContext()

def log(msg):
    """Log to stderr to avoid corrupting MCP stdout stream"""
    print(msg, file=sys.stderr, flush=True)

@mcp.on_startup
async def initialize():
    """Initialize connections on startup"""
    if not GraphClient:
        log("Error: Missing dependencies (GraphClient). Did you run setup.sh?")
        return

    try:
        log("Initializing Grafka components...")

        # 1. Embeddings (CPU friendly default)
        context.embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

        # 2. Vector Store (Local Qdrant)
        context.vector_store = VectorStore()

        # 3. Ontology Service (Load OWL)
        ontology_path = os.path.join(os.getcwd(), "ontology", "core.owl")

        # Initialize RDFLib graph for the reasoner
        try:
            from rdflib import Graph
            g = Graph()
            if os.path.exists(ontology_path):
                g.parse(ontology_path)
                log(f"Loaded ontology from {ontology_path} with {len(g)} triples")
            context.ontology_graph = g
        except Exception as e:
            log(f"Warning: Could not load ontology: {e}")
            context.ontology_graph = None

        # 4. Pipeline Engine (DataSyn)
        context.pipeline_engine = DataSynPipeline()

        # 5. LLM Manager
        context.pipeline_manager = LLMPipelineManager()

        log("Grafka components initialized successfully.")
    except Exception as e:
        log(f"Error initializing Grafka: {e}")

@mcp.tool()
async def query_knowledge_graph(query: str) -> str:
    """
    Query the knowledge graph using RAG (hybrid symbolic + vector search).
    Asks the system to find answers based on stored data.

    Args:
        query: Natural language query (e.g. "What plants improve soil?")
    """
    if not context.pipeline_manager:
        return "Error: System not initialized. Run setup.sh to install dependencies."

    exec_context = {
        "vector_store": context.vector_store,
        "embedder": context.embedder,
        "pipeline_engine": context.pipeline_engine,
        "ontology": context.ontology_graph,
        "tenant_id": "default"
    }

    try:
        # Execute the orchestrated workflow
        result = await context.pipeline_manager.execute(query, exec_context)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
async def extract_knowledge(text: str) -> str:
    """
    Extract facts (triples) from text and add them to the graph.
    Use this when you have new information to learn.

    Args:
        text: The text to analyze and extract from.
    """
    if not context.pipeline_engine:
         return "Error: Pipeline engine not initialized"

    try:
        # Run DataSyn pipeline directly for text
        result = context.pipeline_engine.run_pipeline("DataSyn Processor", text, tenant_id="default")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Extraction failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()
