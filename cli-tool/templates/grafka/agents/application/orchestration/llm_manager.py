"""
LLM Pipeline Manager - Autonomous Agent Orchestrator
Acts as a meta-MCP that can compose and route to other MCP tools
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from agents.domain.services.synthesis_service import FormalIntegrator

class ToolType(Enum):
    """Available tool types"""
    NL2CYPHER = "nl2cypher"
    OWL_REASONING = "owl_reasoning"
    ONTOLOGY_VALIDATION = "ontology_validation"
    PIPELINE_RESEARCH = "pipeline_research"
    PIPELINE_DATASYN = "pipeline_datasyn"
    RAG_SEARCH = "rag_search"
    TRIPLE_EXTRACTION = "triple_extraction"

@dataclass
class ToolCall:
    """Represents a tool invocation"""
    tool: ToolType
    parameters: Dict[str, Any]
    reasoning: str

class LLMPipelineManager:
    """
    Autonomous orchestrator that decides which tools to use.
    Can compose multiple MCP servers and coordinate multi-agent workflows.
    """

    def __init__(self):
        self.available_tools = self._register_tools()
        self.execution_history = []
        self.integrator = FormalIntegrator()

    def _register_tools(self) -> Dict[ToolType, Dict]:
        """Register all available tools with their capabilities"""
        return {
            ToolType.NL2CYPHER: {
                "description": "Translate natural language to Cypher queries for graph traversal",
                "use_when": ["user asks 'what', 'show', 'find', 'which'", "graph query needed"],
                "input": "natural language question",
                "output": "cypher query + results"
            },
            ToolType.OWL_REASONING: {
                "description": "Apply OWL inference rules to expand knowledge",
                "use_when": ["user asks to 'infer', 'reason', 'expand'", "need to derive new facts"],
                "input": "triples to reason over",
                "output": "inferred triples"
            },
            ToolType.ONTOLOGY_VALIDATION: {
                "description": "Validate triples against ontology schema",
                "use_when": ["before storing data", "quality control needed"],
                "input": "triples to validate",
                "output": "valid/invalid triples + suggestions"
            },
            ToolType.PIPELINE_RESEARCH: {
                "description": "CSV → Research → Extract → Validate workflow",
                "use_when": ["processing CSV data", "need research context"],
                "input": "CSV line or filename",
                "output": "extracted triples"
            },
            ToolType.PIPELINE_DATASYN: {
                "description": "Process documents (CSV, MD, JSON) with chunking",
                "use_when": ["large files", "batch processing", "file path given"],
                "input": "file path",
                "output": "extracted triples"
            },
            ToolType.RAG_SEARCH: {
                "description": "Semantic search using vector embeddings",
                "use_when": ["general questions", "concept lookup", "no specific tool matches"],
                "input": "search query",
                "output": "relevant concepts"
            },
            ToolType.TRIPLE_EXTRACTION: {
                "description": "Extract triples from raw text",
                "use_when": ["user provides text to analyze", "simple extraction"],
                "input": "text",
                "output": "triples"
            }
        }

    def decide_tools(self, user_request: str, use_llm: bool = False) -> List[ToolCall]:
        """
        Decide which tools to use for a user request.

        Args:
            user_request: User's natural language request
            use_llm: If True, use LLM for decision. If False, use rules.

        Returns:
            List of tools to execute in order
        """
        if use_llm:
            return self._decide_with_llm(user_request)
        else:
            return self._decide_with_rules(user_request)

    def _decide_with_rules(self, request: str) -> List[ToolCall]:
        """Rule-based tool selection (no LLM required)"""
        request_lower = request.lower()
        tools = []

        # Check for file processing
        if any(ext in request_lower for ext in ['.csv', '.md', '.json']):
            tools.append(ToolCall(
                tool=ToolType.PIPELINE_DATASYN,
                parameters={"input": request},
                reasoning="File path detected, using DataSyn pipeline"
            ))

        # Check for inference request
        elif any(kw in request_lower for kw in ['infer', 'reason', 'expand', 'deduce']):
            tools.append(ToolCall(
                tool=ToolType.OWL_REASONING,
                parameters={"triples": "recent"},
                reasoning="Inference keywords detected"
            ))

        # Check for graph query
        elif any(kw in request_lower for kw in ['what', 'show', 'find', 'which', 'list']):
            tools.append(ToolCall(
                tool=ToolType.NL2CYPHER,
                parameters={"question": request},
                reasoning="Query keywords detected"
            ))

        # Check for extraction
        elif 'extract' in request_lower or len(request.split()) > 10:
            tools.append(ToolCall(
                tool=ToolType.TRIPLE_EXTRACTION,
                parameters={"text": request},
                reasoning="Text extraction needed"
            ))

        # Default to RAG search
        else:
            tools.append(ToolCall(
                tool=ToolType.RAG_SEARCH,
                parameters={"query": request},
                reasoning="General question, using semantic search"
            ))

        return tools

    def _decide_with_llm(self, request: str) -> List[ToolCall]:
        """LLM-based tool selection with reasoning"""
        try:
            from litellm import completion
            import os
        except ImportError:
            print("⚠️ litellm not available, falling back to rules")
            return self._decide_with_rules(request)

        # Build prompt with tool descriptions
        tools_desc = "\n".join([
            f"- {tool.value}: {info['description']}\n  Use when: {', '.join(info['use_when'])}"
            for tool, info in self.available_tools.items()
        ])

        prompt = f"""You are an autonomous agent orchestrator. Analyze the user request and decide which tools to use.

Available Tools:
{tools_desc}

User Request: "{request}"

Respond with JSON:
{{
    "tools": [
        {{
            "tool": "tool_name",
            "parameters": {{}},
            "reasoning": "why this tool"
        }}
    ]
}}

You can select multiple tools if needed (they'll execute in sequence).
"""

        try:
            response = completion(
                model=os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            result = json.loads(response.choices[0].message.content)

            # Convert to ToolCall objects
            tools = []
            for t in result.get("tools", []):
                try:
                    tool_type = ToolType(t["tool"])
                    tools.append(ToolCall(
                        tool=tool_type,
                        parameters=t.get("parameters", {}),
                        reasoning=t.get("reasoning", "")
                    ))
                except ValueError:
                    continue

            return tools if tools else self._decide_with_rules(request)

        except Exception as e:
            print(f"LLM decision failed: {e}")
            return self._decide_with_rules(request)

    async def execute(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the orchestrated workflow.

        Args:
            user_request: User's request
            context: Execution context (ontology, clients, etc.)

        Returns:
            Execution results with synthesized answer.
        """
        # Decide which tools to use
        tool_calls = self.decide_tools(user_request, use_llm=False)

        results = {
            "request": user_request,
            "tools_used": [],
            "outputs": [],
            "success": True
        }

        # Execute each tool
        for tool_call in tool_calls:
            tool_result = await self._execute_tool(tool_call, context)

            results["tools_used"].append({
                "tool": tool_call.tool.value,
                "reasoning": tool_call.reasoning
            })
            results["outputs"].append(tool_result)

            # Store in execution history
            self.execution_history.append({
                "request": user_request,
                "tool": tool_call.tool.value,
                "result": tool_result
            })

        # FORMAL INTEGRATION STEP (FI)
        # Synthesize logic into final answer
        try:
            synthesized_answer = await self.integrator.synthesize(user_request, results["outputs"])
            results["final_answer"] = synthesized_answer
        except Exception as e:
            print(f"Synthesis failed: {e}")
            results["final_answer"] = "Error synthesizing answer."

        return results

    async def _execute_tool(self, tool_call: ToolCall, context: Dict) -> Any:
        """Execute a single tool"""
        tool = tool_call.tool
        params = tool_call.parameters

        if tool == ToolType.NL2CYPHER:
            from agents.tools.nl2cypher import NL2CypherAgent
            from agents.tools.cypher_executor import CypherExecutor

            agent = NL2CypherAgent()
            cypher = await agent.translate(params.get("question", ""), use_llm=False)

            if cypher:
                executor = CypherExecutor()
                return executor.execute(cypher)
            return {"error": "Could not translate to Cypher"}

        elif tool == ToolType.OWL_REASONING:
            from agents.tools.owl_reasoner import OWLReasoningAgent

            reasoner = OWLReasoningAgent(context["ontology"])
            triples = context.get("stored_triples", [])[-10:]
            return reasoner.infer(triples)

        elif tool == ToolType.RAG_SEARCH:
            embedder = context["embedder"]
            vector_store = context["vector_store"]
            tenant_id = context.get("tenant_id")

            query_emb = embedder.encode_single(params.get("query", ""))
            results = vector_store.search(query_emb, top_k=3, tenant_id=tenant_id)
            return {"results": [r.metadata for r in results]}

        elif tool == ToolType.PIPELINE_DATASYN:
            pipeline_engine = context["pipeline_engine"]
            tenant_id = context.get("tenant_id", "default")
            return pipeline_engine.run_pipeline("DataSyn Processor", params.get("input", ""), tenant_id=tenant_id)

        else:
            return {"error": f"Tool {tool.value} not yet implemented"}

    def get_tool_description(self, tool: ToolType) -> str:
        """Get human-readable tool description"""
        info = self.available_tools.get(tool, {})
        return f"**{tool.value}**: {info.get('description', 'N/A')}"

    def get_execution_summary(self) -> str:
        """Get summary of recent executions"""
        if not self.execution_history:
            return "No executions yet"

        summary = f"**Recent Executions:** {len(self.execution_history)}\n\n"
        for i, exec in enumerate(self.execution_history[-5:], 1):
            summary += f"{i}. Tool: {exec['tool']}\n"
            summary += f"   Request: {exec['request'][:50]}...\n"

        return summary
