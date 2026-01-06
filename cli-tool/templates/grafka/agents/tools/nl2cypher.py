"""
NL2Cypher Agent - Natural Language to Cypher Query Translation
Optimized with Agent Lightning's AIR system
"""
from typing import Dict, List, Tuple, Optional
from agents.infrastructure.ai.air import get_air, RewardSignal
import os
import re

class NL2CypherAgent:
    """
    Translates natural language questions to Cypher queries
    for the triple-based knowledge graph.

    Uses few-shot learning with Agent Lightning optimization.
    """

    def __init__(self):
        self.air = get_air()
        self.few_shot_examples = self._load_examples()

        # Init schema validator
        try:
            from agents.domain.services.ontology import OntologyService
            from agents.validation.ontology_validator import OntologyValidator
            self.ontology_service = OntologyService(["ontology/core.owl", "ontology/agriculture.owl"])
            self.validator = OntologyValidator(self.ontology_service)
        except Exception as e:
            print(f"⚠️ Failed to load ontology for NL2Cypher: {e}")
            self.validator = None

    def _load_examples(self) -> List[Dict[str, str]]:
        """Few-shot examples for NL → Cypher translation"""
        return [
            {
                "question": "What plants are in the Rosaceae family?",
                "cypher": "MATCH (p)-[:belongsTo]->(f) WHERE f = 'Rosaceae' RETURN p"
            },
            {
                "question": "Show me all swales that capture water",
                "cypher": "MATCH (s)-[:captures]->(w) WHERE s CONTAINS 'Swale' AND w CONTAINS 'Water' RETURN s, w"
            },
            {
                "question": "What improves soil?",
                "cypher": "MATCH (x)-[:improves]->(s) WHERE s CONTAINS 'Soil' RETURN x"
            },
            {
                "question": "Find all plants with height greater than 5m",
                "cypher": "MATCH (p)-[:height]->(h) WHERE p CONTAINS 'Plant' AND h > '5' RETURN p, h"
            },
            {
                "question": "What is connected to FoodForest?",
                "cypher": "MATCH (f)-[r]-(x) WHERE f = 'FoodForest' RETURN x, type(r)"
            }
        ]

    async def translate(self, question: str, use_llm: bool = False) -> Optional[str]:
        """
        Translate natural language to Cypher query.

        Args:
            question: Natural language question
            use_llm: If True, use LLM (requires API key). If False, use pattern matching.

        Returns:
            Cypher query string or None if translation fails
        """
        self.air.reset()

        cypher = None
        if use_llm:
            cypher = await self._translate_with_llm(question)
        else:
            cypher = self._translate_with_patterns(question)

        # Verify schema
        if cypher and self.validator:
            cypher = self._verify_and_fix_schema(cypher)

        return cypher

    def _translate_with_patterns(self, question: str) -> Optional[str]:
        """Simple pattern-based translation (no LLM required)"""
        q_lower = question.lower()

        # Pattern 1: "What X verb Y?"
        if "what" in q_lower and "improve" in q_lower:
            if "soil" in q_lower:
                cypher = "MATCH (x)-[:improves]->(s) WHERE s CONTAINS 'Soil' RETURN x"
                self.air.record_event(RewardSignal.QUERY_GENERATED, {"pattern": "what_improves"})
                return cypher

        # Pattern 2: "Show me X that verb Y"
        if "show" in q_lower or "find" in q_lower:
            if "swale" in q_lower and "water" in q_lower:
                cypher = "MATCH (s)-[:captures]->(w) WHERE s CONTAINS 'Swale' RETURN s, w"
                self.air.record_event(RewardSignal.QUERY_GENERATED, {"pattern": "show_swale"})
                return cypher

        # Pattern 3: "What is X?" (find all relationships)
        if "what is" in q_lower or "tell me about" in q_lower:
            # Extract entity name
            words = question.split()
            entity = words[-1].rstrip('?').strip()
            cypher = f"MATCH (n)-[r]-(m) WHERE n = '{entity}' RETURN n, type(r), m LIMIT 20"
            self.air.record_event(RewardSignal.QUERY_GENERATED, {"pattern": "what_is", "entity": entity})
            return cypher

        # Pattern 4: Generic search
        # Extract key nouns and create a general query
        keywords = [w for w in q_lower.split() if len(w) > 3 and w not in ['what', 'show', 'find', 'that', 'the']]
        if keywords:
            keyword = keywords[0].capitalize()
            cypher = f"MATCH (n)-[r]-(m) WHERE n CONTAINS '{keyword}' OR m CONTAINS '{keyword}' RETURN n, type(r), m LIMIT 10"
            self.air.record_event(RewardSignal.QUERY_GENERATED, {"pattern": "generic", "keyword": keyword})
            return cypher

        # Failed to translate
        self.air.record_error("no_pattern_match")
        return None

    async def _translate_with_llm(self, question: str) -> Optional[str]:
        """LLM-based translation with few-shot prompting"""
        try:
            from litellm import acompletion
        except ImportError:
            print("⚠️ litellm not available, falling back to pattern matching")
            return self._translate_with_patterns(question)

        # Build few-shot prompt
        examples_text = "\n\n".join([
            f"Question: {ex['question']}\nCypher: {ex['cypher']}"
            for ex in self.few_shot_examples
        ])

        prompt = f"""You are a Cypher query generator for a knowledge graph of triples.
The graph stores (subject, predicate, object) triples.

Examples:
{examples_text}

Now translate this question to Cypher:
Question: {question}
Cypher:"""

        try:
            response = await acompletion(
                model=os.getenv("GEMINI_MODEL", "gemini-3-flash"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )

            cypher = response.choices[0].message.content.strip()

            # AIR: Reward for successful LLM call
            self.air.record_event(RewardSignal.QUERY_GENERATED, {"method": "llm"})
            self.air.record_token_usage(response.usage.total_tokens)

            return cypher

        except Exception as e:
            print(f"LLM translation failed: {e}")
            self.air.record_error("llm_failed")
            return self._translate_with_patterns(question)

    def _verify_and_fix_schema(self, cypher: str) -> str:
        """
        Verify that predicates in Cypher exist in ontology.
        If not, replace with closest match.
        """
        # 1. Check Relationship Types: [:TYPE] or [r:TYPE]
        # Pattern: : followed by word characters, INSIDE square brackets
        # We can approximate by looking for :Type followed by ]
        # Or better: use a regex that finds all :Word patterns and checks context

        # Naive implementation improved:
        # Split by non-word chars to find tokens, then check context

        fixed_cypher = cypher
        changes_made = False

        # Find all relationships
        # Matches [:RelType] or [r:RelType]
        rel_matches = re.finditer(r"\[[^\]]*:(\w+)[^\]]*\]", cypher)

        for match in rel_matches:
            rel_type = match.group(1)
            if not self.validator._is_valid_property(rel_type):
                suggestion = self.validator._find_closest_match(rel_type, self.validator.valid_properties)
                if suggestion:
                    print(f"  🔧 Auto-correcting relationship: {rel_type} -> {suggestion}")
                    # Replace only this occurrence
                    fixed_cypher = fixed_cypher.replace(f":{rel_type}", f":{suggestion}")
                    changes_made = True

        # Find all Node Labels
        # Matches (:Label) or (n:Label)
        label_matches = re.finditer(r"\([^\)]*:(\w+)[^\)]*\)", cypher)

        for match in label_matches:
            label = match.group(1)
            if not self.validator._is_valid_entity(label):
                suggestion = self.validator._find_closest_match(label, self.validator.valid_classes)
                if suggestion:
                    print(f"  🔧 Auto-correcting label: {label} -> {suggestion}")
                    fixed_cypher = fixed_cypher.replace(f":{label}", f":{suggestion}")
                    changes_made = True

        if changes_made:
            self.air.record_event(RewardSignal.OWL_CONSISTENT, {"action": "schema_correction"})

        return fixed_cypher

    def validate_cypher(self, cypher: str) -> bool:
        """Basic Cypher syntax validation"""
        if not cypher:
            return False

        # Check for required keywords
        has_match = "MATCH" in cypher.upper()
        has_return = "RETURN" in cypher.upper()

        if has_match and has_return:
            self.air.record_event(RewardSignal.QUERY_VALID)
            return True
        else:
            self.air.record_error("invalid_cypher_syntax")
            return False

    def get_reward_summary(self) -> str:
        """Get AIR reward summary"""
        return self.air.get_summary()
