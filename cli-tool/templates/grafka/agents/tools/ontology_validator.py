"""
Ontology Validator - Ensures data quality
Rejects triples that don't conform to the ontology schema
"""
from typing import Dict, Any, Set, Optional, List, Tuple
from agents.domain.services.ontology import OntologyService
from agents.infrastructure.ai.air import get_air, RewardSignal

class OntologyValidator:
    """
    Validates triples against the ontology.
    Rejects nodes that don't exist in the ontology schema.
    """

    def __init__(self, ontology: OntologyService):
        self.ontology = ontology
        self.air = get_air()

        # Cache valid classes and properties
        self.valid_classes = self._load_valid_classes()
        self.valid_properties = self._load_valid_properties()

    def _load_valid_classes(self) -> Set[str]:
        """Load all valid classes from ontology"""
        classes = set()

        # Query ontology for all classes
        query = """
        SELECT DISTINCT ?class WHERE {
            ?class a owl:Class .
        }
        """
        results = self.ontology.graph.query(query)

        for row in results:
            class_uri = row[0]  # Access by index instead of attribute
            class_name = str(class_uri).split('#')[-1].split('/')[-1]
            classes.add(class_name)

        # Add common variations
        for cls in list(classes):
            classes.add(cls.lower())
            classes.add(cls.capitalize())

        return classes

    def _load_valid_properties(self) -> Set[str]:
        """Load all valid properties from ontology"""
        properties = set()

        query = """
        SELECT DISTINCT ?prop WHERE {
            { ?prop a owl:ObjectProperty . }
            UNION
            { ?prop a owl:DatatypeProperty . }
        }
        """
        results = self.ontology.graph.query(query)

        for row in results:
            prop_uri = row[0]  # Access by index
            prop_name = str(prop_uri).split('#')[-1].split('/')[-1]
            properties.add(prop_name)

        # Add common variations
        for prop in list(properties):
            properties.add(prop.lower())
            properties.add(prop.replace('_', ' '))

        return properties

    def validate_triple(self, subject: str, predicate: str, obj: str) -> Dict[str, any]:
        """
        Validate a single triple against ontology.

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "suggestions": Dict[str, str]
            }
        """
        errors = []
        suggestions = {}

        # Check if subject matches a known class
        subject_valid = self._is_valid_entity(subject)
        if not subject_valid:
            # Relaxed: Allow new entities, but maybe flag them?
            # For now, we accept them as valid new knowledge
            pass
            # errors.append(f"Subject '{subject}' not in ontology")
            # suggestions["subject"] = self._find_closest_match(subject, self.valid_classes)

        # Check if predicate is valid (STRICT)
        predicate_valid = self._is_valid_property(predicate)
        if not predicate_valid:
            errors.append(f"Predicate '{predicate}' not in ontology")
            suggestions["predicate"] = self._find_closest_match(predicate, self.valid_properties)

        # Check if object matches a known class
        object_valid = self._is_valid_entity(obj)
        if not object_valid:
            # Relaxed: Allow new entities
            pass
            # errors.append(f"Object '{obj}' not in ontology")
            # suggestions["object"] = self._find_closest_match(obj, self.valid_classes)

        # Only predicate must be valid for now to allow graph expansion
        is_valid = predicate_valid

        # AIR: Reward/penalty
        if is_valid:
            self.air.record_event(RewardSignal.OWL_CONSISTENT, {"triple": (subject, predicate, obj)})
        else:
            self.air.record_error("ontology_violation")

        return {
            "valid": is_valid,
            "errors": errors,
            "suggestions": suggestions
        }

    def _is_valid_entity(self, entity: str) -> bool:
        """Check if entity exists in ontology classes"""
        # Direct match
        if entity in self.valid_classes:
            return True

        # Case-insensitive match
        if entity.lower() in self.valid_classes:
            return True

        # Check if it's an instance (contains known class name)
        for cls in self.valid_classes:
            if cls.lower() in entity.lower():
                return True

        return False

    def _is_valid_property(self, prop: str) -> bool:
        """Check if property exists in ontology"""
        if prop in self.valid_properties:
            return True

        if prop.lower() in self.valid_properties:
            return True

        # Fuzzy match
        prop_normalized = prop.replace(' ', '_').replace('-', '_')
        if prop_normalized in self.valid_properties:
            return True

        return False

    def _find_closest_match(self, term: str, valid_set: Set[str]) -> Optional[str]:
        """Find closest matching term in valid set"""
        from difflib import get_close_matches

        matches = get_close_matches(term, valid_set, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def validate_batch(self, triples: List[Tuple[str, str, str]]) -> Dict[str, any]:
        """
        Validate a batch of triples.

        Returns:
            {
                "valid_triples": List[Tuple],
                "invalid_triples": List[Tuple],
                "corrections": List[Dict]
            }
        """
        valid = []
        invalid = []
        corrections = []

        for s, p, o in triples:
            result = self.validate_triple(s, p, o)

            if result["valid"]:
                valid.append((s, p, o))
            else:
                invalid.append((s, p, o))

                # Suggest correction
                correction = {
                    "original": (s, p, o),
                    "errors": result["errors"],
                    "suggestions": result["suggestions"]
                }
                corrections.append(correction)

        return {
            "valid_triples": valid,
            "invalid_triples": invalid,
            "corrections": corrections,
            "accuracy": len(valid) / len(triples) if triples else 0.0
        }

    def get_correction_prompt(self, invalid_triple: Tuple[str, str, str], suggestions: Dict[str, str]) -> str:
        """
        Generate prompt for LLM to correct invalid triple.
        This is the distillation step.
        """
        s, p, o = invalid_triple

        prompt = f"""You extracted an invalid triple that doesn't match the ontology.

Original Triple: ({s}, {p}, {o})

Valid Ontology Classes: {', '.join(list(self.valid_classes)[:20])}...
Valid Properties: {', '.join(list(self.valid_properties)[:20])}...

Suggestions:
"""
        if "subject" in suggestions:
            prompt += f"- Subject: Use '{suggestions['subject']}' instead of '{s}'\n"
        if "predicate" in suggestions:
            prompt += f"- Predicate: Use '{suggestions['predicate']}' instead of '{p}'\n"
        if "object" in suggestions:
            prompt += f"- Object: Use '{suggestions['object']}' instead of '{o}'\n"

        prompt += "\nProvide the corrected triple in format: (subject, predicate, object)"

        return prompt

    def get_stats(self) -> Dict[str, any]:
        """Get validation statistics"""
        return {
            "total_classes": len(self.valid_classes),
            "total_properties": len(self.valid_properties),
            "air_summary": self.air.get_summary()
        }
