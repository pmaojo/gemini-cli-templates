"""
Research Pipeline Strategy
Implements the workflow: CSV Line -> Research (Search/RAG) -> Extraction -> Triples
"""
import time
from typing import Any, List, Dict
from .engine import PipelineStrategy, PipelineResult
# Import agents (using mocks/stubs for speed in this demo, but designed to swap)
# from ..inference.slm import TrainableSLM

class ResearchPipeline(PipelineStrategy):
    """
    Investigates a topic from a CSV line and extracts knowledge.
    """
    def __init__(self, slm=None, translation_service=None):
        self.slm = slm
        self.translation_service = translation_service

    @property
    def name(self) -> str:
        return "Research & Extraction"

    def run(self, input_data: str, **kwargs) -> PipelineResult:
        """
        Args:
            input_data: A string representing a CSV line or query (e.g., "Apple Tree, Guild, Permaculture")
            kwargs: Additional arguments
        """
        logs = []
        logs.append(f"📥 Input received: '{input_data}'")

        # TRANSLATION STEP (Global Layer)
        if self.translation_service:
            logs.append("🌍 Translating input...")
            input_data = self.translation_service.translate(input_data)
            logs.append(f"🇬🇧 English Input: '{input_data}'")

        # Step 1: Parse Input
        keywords = [k.strip() for k in input_data.split(',')]
        logs.append(f"🔍 Keywords identified: {keywords}")

        # Step 2: Simulate Research (Retrieval)
        # In a real system, this would call Google Search or RAG
        logs.append("🌐 Searching literature...")
        found_text = self._mock_search(keywords)
        logs.append(f"📄 Found context ({len(found_text)} chars)")

        # Step 3: Extraction (SLM)
        # Using rule-based mock for speed/reliability in this demo context
        logs.append("🤖 Extracting triples with SLM...")
        triples = self._mock_extraction(found_text, keywords)
        logs.append(f"✨ Extracted {len(triples)} triples")

        # Step 4: Action Linking (Mock)
        actions = []
        if len(triples) > 0:
            actions.append("Trigger: Update Knowledge Graph")
            actions.append(f"Trigger: Notify User ({len(triples)} new facts)")

        return PipelineResult(
            success=True,
            data={
                "triples": triples,
                "source_text": found_text[:200] + "...",
                "actions_triggered": actions
            },
            logs=logs,
            execution_time=0.0 # Calculated by engine
        )

    def _mock_search(self, keywords: List[str]) -> str:
        """Simulate finding relevant text based on keywords"""
        # Dictionary of "knowledge" for the demo
        knowledge_base = {
            "apple": "Apple trees (Malus domestica) grow best in guilds with comfrey, daffodils, and nitrogen fixers like clover. They require cross-pollination.",
            "compost": "Compost is organic matter that has been decomposed. It improves soil structure, provides nutrients, and increases water retention.",
            "swale": "A swale is a water-harvesting ditch on contour. It stops water flow, spreads it horizontally, and sinks it into the ground.",
            "guild": "A guild is a beneficial grouping of plants that support each other. Common functions include nitrogen fixation, mulch production, and pollinator attraction."
        }

        results = []
        for k in keywords:
            k_lower = k.lower()
            for key, text in knowledge_base.items():
                if key in k_lower:
                    results.append(text)

        if not results:
            return "No specific literature found for these terms. General permaculture principles apply."

        return " ".join(results)

    def _mock_extraction(self, text: str, keywords: List[str]) -> List[str]:
        """Extract triples using SLM if available, else mock"""
        if self.slm:
            try:
                # Use the same prompt strategy as the UI
                prompt = f"""Eres un experto en agricultura regenerativa. Extrae triples RDF del texto.
Formato JSON: [["sujeto", "predicado", "objeto"]]

Input: {text[:1000]}
Output:"""
                generated = self.slm.generate(prompt, max_new_tokens=128)

                import json
                import re
                json_match = re.search(r'\[\s*\[.*?\]\s*\]', generated, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception as e:
                print(f"⚠️ Pipeline SLM Error: {e}")

        # Fallback to mock if SLM fails or not provided
        triples = []
        text_lower = text.lower()

        if "apple" in text_lower:
            triples.append(["AppleTree", "growsIn", "Guild"])
            triples.append(["AppleTree", "requires", "Pollination"])
        if "comfrey" in text_lower:
            triples.append(["Comfrey", "isA", "DynamicAccumulator"])
        if "clover" in text_lower:
            triples.append(["Clover", "fixes", "Nitrogen"])
        if "compost" in text_lower:
            triples.append(["Compost", "improves", "SoilStructure"])
        if "swale" in text_lower:
            triples.append(["Swale", "harvests", "Water"])

        return triples
