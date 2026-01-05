"""
Ontogenia Ontology Generation Pipeline
Implements the 'Ontogenia' technique for ontology generation.
"""
import time
import json
import re
from typing import Any, List, Dict
from .engine import PipelineStrategy, PipelineResult

class OntologyGenerationPipeline(PipelineStrategy):
    """
    Generates an ontology from a domain description using a multi-step prompting strategy.
    """
    def __init__(self, slm=None, translation_service=None):
        self.slm = slm
        self.translation_service = translation_service

    @property
    def name(self) -> str:
        return "Ontogenia Generation"

    def run(self, input_data: str, **kwargs) -> PipelineResult:
        """
        Args:
            input_data: A string description of the domain (e.g., "Regenerative Agriculture in arid climates")
            kwargs: Additional arguments
        """
        logs = []
        logs.append(f"📥 Domain Description: '{input_data}'")

        # TRANSLATION STEP
        if self.translation_service:
            logs.append("🌍 Translating input...")
            input_data = self.translation_service.translate(input_data)
            logs.append(f"🇬🇧 English Input: '{input_data}'")

        # Step 1: Generate Core Classes
        logs.append("🏗️ Step 1: Identifying Core Classes...")
        classes = self._generate_classes(input_data)
        logs.append(f"✅ Identified {len(classes)} classes: {', '.join(classes[:5])}...")

        # Step 2: Generate Properties (Relations)
        logs.append("🔗 Step 2: Defining Relationships...")
        relationships = self._generate_relationships(input_data, classes)
        logs.append(f"✅ Defined {len(relationships)} relationships")

        # Step 3: Format as Ontology (JSON-LD or similar internal format)
        ontology_structure = {
            "domain": input_data,
            "classes": [{"id": c, "label": c} for c in classes],
            "properties": relationships
        }

        return PipelineResult(
            success=True,
            data={
                "ontology": ontology_structure,
                "summary": f"Generated {len(classes)} classes and {len(relationships)} relationships."
            },
            logs=logs,
            execution_time=0.0
        )

    def _generate_classes(self, domain: str) -> List[str]:
        """Generate a list of core classes for the domain"""
        if self.slm:
            prompt = f"""Identify the top 10 core concepts (classes) for an ontology about: {domain}.
Output as a JSON list of strings.
Example: ["Concept1", "Concept2"]
Output:"""
            try:
                generated = self.slm.generate(prompt, max_new_tokens=128)
                json_match = re.search(r'\[.*?\]', generated, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except Exception as e:
                print(f"⚠️ SLM Class Generation Error: {e}")

        # Mock/Fallback
        return ["ConceptA", "ConceptB", "ConceptC", "System", "Process"]

    def _generate_relationships(self, domain: str, classes: List[str]) -> List[Dict]:
        """Generate relationships between classes"""
        relationships = []
        if self.slm:
            classes_str = ", ".join(classes[:5]) # Use top 5 for prompt context
            prompt = f"""Define relationships between these concepts: {classes_str}.
Context: {domain}.
Output as JSON list of triples [subject, predicate, object].
Output:"""
            try:
                generated = self.slm.generate(prompt, max_new_tokens=256)
                json_match = re.search(r'\[\s*\[.*?\]\s*\]', generated, re.DOTALL)
                if json_match:
                    triples = json.loads(json_match.group(0))
                    for s, p, o in triples:
                        relationships.append({"source": s, "target": o, "relation": p})
                    return relationships
            except Exception as e:
                print(f"⚠️ SLM Relation Generation Error: {e}")

        # Mock/Fallback
        if len(classes) >= 2:
            relationships.append({"source": classes[0], "target": classes[1], "relation": "relatedTo"})
            relationships.append({"source": classes[1], "target": classes[0], "relation": "dependsOn"})

        return relationships
