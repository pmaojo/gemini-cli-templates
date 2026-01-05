"""
Formal Integration Service
Synthesizes structured logic and data into natural language answers.
Implements the 'Formal Integration' (FI) step of the pipeline.
"""
from typing import List, Dict, Any, Optional
import os
import json

class FormalIntegrator:
    """
    Integrates logical deductions, extracted triples, and RAG context
    into a coherent natural language response.
    """

    def __init__(self, slm=None):
        self.slm = slm

    async def synthesize(self, question: str, tool_results: List[Dict[str, Any]]) -> str:
        """
        Synthesize a final answer from tool outputs.

        Args:
            question: The user's original question.
            tool_results: List of outputs from executed tools.

        Returns:
            A natural language string answering the question based on the evidence.
        """
        # 1. Aggregate Evidence
        evidence_text = self._format_evidence(tool_results)

        if not evidence_text:
            return "I couldn't find any specific information to answer your question based on the tools used."

        # 2. Generate Answer
        answer = await self._generate_with_llm(question, evidence_text)

        return answer

    def _format_evidence(self, tool_results: List[Dict[str, Any]]) -> str:
        """Format raw tool outputs into a readable evidence string"""
        evidence_parts = []

        for i, result in enumerate(tool_results, 1):
            if "error" in result:
                continue

            part = self._format_result_part(result)
            if part:
                evidence_parts.append(part)

        return "\n\n".join(evidence_parts)

    def _format_result_part(self, result: Any) -> Optional[str]:
        """Format a single tool result into a string part"""
        if isinstance(result, dict):
            if "inferred_triples" in result:
                return self._format_owl_result(result)
            if "results" in result:
                return self._format_search_result(result)
            return f"Tool Output:\n{json.dumps(result, default=str)[:500]}"

        if isinstance(result, list):
            str_repr = str(result)[:500]
            return f"Graph Data:\n{str_repr}"

        return None

    def _format_owl_result(self, result: Dict[str, Any]) -> Optional[str]:
        """Format OWL reasoning output"""
        triples = result.get("inferred_triples", [])
        rules = result.get("rules_applied", {})
        if not triples:
            return None
        triples_str = ", ".join([f"({s}, {p}, {o})" for s, p, o in triples[:10]])
        return f"Logical Deductions (OWL):\n- Inferred Facts: {triples_str}\n- Rules Applied: {json.dumps(rules)}"

    def _format_search_result(self, result: Dict[str, Any]) -> Optional[str]:
        """Format RAG/Search output"""
        items = result.get("results", [])
        if not items:
            return None
        texts = []
        for item in items:
            if isinstance(item, dict):
                desc = item.get("description") or item.get("content") or str(item)
                texts.append(desc[:200])
        if not texts:
            return None
        return "Search Results (Context):\n" + "\n".join([f"- {t}" for t in texts])

    async def _generate_with_llm(self, question: str, evidence: str) -> str:
        """Generate response using LLM"""
        try:
            from litellm import acompletion
        except ImportError:
            return self._fallback_synthesis(question, evidence)

        prompt = f"""You are the 'Formal Integration' module of a neuro-symbolic AI.
Your job is to synthesize a final answer based ONLY on the provided evidence (Logical Deductions, Graph Data, Context).

User Question: "{question}"

Evidence collected:
{evidence}

Instructions:
1. Answer the question directly using the evidence.
2. Explicitly mention if the answer was derived via "Logical Deduction" or "Reasoning" (if OWL evidence exists).
3. If the evidence is insufficient, say so.
4. Keep it concise (under 4 sentences if possible).

Answer:"""

        try:
            response = await acompletion(
                model=os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Synthesis LLM failed: {e}")
            return self._fallback_synthesis(question, evidence)

    def _fallback_synthesis(self, question: str, evidence: str) -> str:
        """Fallback if LLM is unavailable"""
        _ = question  # Silence unused parameter warning
        return f"**Analysis based on evidence:**\n\n{evidence}\n\n(Note: LLM synthesis unavailable, showing raw evidence)"
