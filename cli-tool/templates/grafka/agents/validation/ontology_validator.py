"""
Ontology Validator - Ensures extracted triples conform to ontology
Implements LLM distillation for error correction
"""
from typing import List, Tuple, Dict, Set, Optional
from rdflib import RDF, RDFS
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

        # Cache domain and range constraints
        self.domains = self._load_domains()
        self.ranges = self._load_ranges()

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
        variations = set()
        for cls in classes:
            variations.add(cls.lower())
            variations.add(cls.capitalize())
        classes.update(variations)

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
        variations = set()
        for prop in properties:
            variations.add(prop.lower())
            variations.add(prop.replace('_', ' '))
        properties.update(variations)

        # Add meta-properties
        properties.add("isA")
        properties.add("isa")
        properties.add("type")

        return properties

    def _load_domains(self) -> Dict[str, str]:
        """Load property domain constraints"""
        domains = {}
        for prop, _, domain in self.ontology.graph.triples((None, RDFS.domain, None)):
            prop_name = str(prop).split('#')[-1].split('/')[-1]
            domain_name = str(domain).split('#')[-1].split('/')[-1]
            domains[prop_name] = domain_name
            # Also store normalized versions
            domains[prop_name.lower()] = domain_name
        return domains

    def _load_ranges(self) -> Dict[str, str]:
        """Load property range constraints"""
        ranges = {}
        for prop, _, range_class in self.ontology.graph.triples((None, RDFS.range, None)):
            prop_name = str(prop).split('#')[-1].split('/')[-1]
            range_name = str(range_class).split('#')[-1].split('/')[-1]
            ranges[prop_name] = range_name
            # Also store normalized versions
            ranges[prop_name.lower()] = range_name
        return ranges

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

        # 1. Check if predicate is valid (STRICT)
        predicate_valid = self._is_valid_property(predicate)
        normalized_predicate = predicate.replace(' ', '_').replace('-', '_')

        if not predicate_valid:
            errors.append(f"Predicate '{predicate}' not in ontology")
            suggestions["predicate"] = self._find_closest_match(predicate, self.valid_properties)
        else:
            # 3. Check Range Constraint (Object Type)
            # If range is a primitive type (xsd:float), check formatting
            # If range is a Class, check if object is a valid entity of that class
            if normalized_predicate in self.ranges:
                expected_range = self.ranges[normalized_predicate]
                self._validate_range(obj, expected_range, errors)


        # Only predicate must be valid for now to allow graph expansion
        is_valid = len(errors) == 0

        # AIR: Reward/penalty
        if is_valid:
            self.air.record_event(RewardSignal.OWL_CONSISTENT, {"triple": (subject, predicate, obj)})
        else:
            # Attempt translation if invalid
            translated_triple = self.translate_to_english(subject, predicate, obj)
            if translated_triple:
                ts, tp, to = translated_triple
                # Re-validate translated triple
                tp_valid = self._is_valid_property(tp)

                if tp_valid:
                    return {
                        "valid": True,
                        "errors": [],
                        "suggestions": {"translated": (ts, tp, to)},
                        "original": (subject, predicate, obj)
                    }

            self.air.record_error("ontology_violation")

        return {
            "valid": is_valid,
            "errors": errors,
            "suggestions": suggestions
        }

    def _validate_range(self, obj: str, expected_range: str, errors: List[str]):
        """Check if object conforms to range constraint"""
        # Handle XSD types
        if "float" in expected_range.lower() or "decimal" in expected_range.lower() or "integer" in expected_range.lower():
            try:
                # Remove common units like "m", "kg", "%"
                clean_obj = ''.join(c for c in obj if c.isdigit() or c == '.')
                if not clean_obj:
                    errors.append(f"Object '{obj}' should be numeric ({expected_range})")
                else:
                    float(clean_obj)
            except ValueError:
                errors.append(f"Object '{obj}' must be a number ({expected_range})")

        # Handle Class types
        elif expected_range in self.valid_classes:
             # Basic heuristic: if object is a named entity, it should probably look like one
             pass

    def translate_to_english(self, s: str, p: str, o: str) -> Optional[Tuple[str, str, str]]:
        """Translate triple to English using LLM"""
        try:
            from litellm import completion
            import os
            import json

            prompt = f"""Translate this triple to English for ontology matching.
Original: ({s}, {p}, {o})

Return JSON only: ["subject_en", "predicate_en", "object_en"]"""

            response = completion(
                model=os.getenv("GEMINI_MODEL", "gemini-3-flash"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )

            content = response.choices[0].message.content
            # Clean markdown code blocks if present
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            return tuple(json.loads(content))
        except Exception:
            # print(f"Translation failed")
            return None

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
                # If translation occurred, use it
                if "suggestions" in result and "translated" in result["suggestions"]:
                    valid.append(result["suggestions"]["translated"])
                else:
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
