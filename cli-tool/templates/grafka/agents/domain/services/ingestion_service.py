"""
Ingestion Service
Unified entry point for all triple ingestion with validation, deduplication,
enrichment, and provenance tracking.
"""
import hashlib
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from agents.validation.ontology_validator import OntologyValidator
from agents.tools.owl_reasoner import OWLReasoningAgent

class IngestionService:
    def __init__(self, ontology_service, rust_client, owl_reasoner=None):
        self.ontology = ontology_service
        self.rust_client = rust_client
        self.validator = OntologyValidator(ontology_service)
        self.reasoner = owl_reasoner
        self.seen_hashes = set()  # For deduplication

        print("📥 Ingestion Service initialized")

    def ingest(self,
               triples: List[Tuple[str, str, str]],
               source: str = "unknown",
               metadata: Optional[Dict[str, Any]] = None,
               skip_enrichment: bool = False,
               tenant_id: str = "default") -> Dict[str, Any]:
        """
        Main ingestion entry point.

        Args:
            triples: List of (subject, predicate, object) tuples
            source: Origin identifier (e.g., "CSV:plants.csv:row_5", "UI:Tab1")
            metadata: Additional context (timestamp, confidence, etc.)
            skip_enrichment: If True, skip OWL reasoning step
            tenant_id: Tenant ID for isolation

        Returns:
            Dictionary with ingestion statistics
        """
        if not triples:
            return {"status": "empty", "stored": 0}

        stats = {
            "input": len(triples),
            "validated": 0,
            "duplicates": 0,
            "enriched": 0,
            "stored": 0,
            "errors": []
        }

        # 1. VALIDATION
        validated_triples = self._validate(triples, stats)

        # 2. DEDUPLICATION
        unique_triples = self._deduplicate(validated_triples, stats)

        # 3. SEMANTIC ENRICHMENT (Optional)
        if not skip_enrichment and self.reasoner and unique_triples:
            enriched_triples = self._enrich(unique_triples, stats)
        else:
            enriched_triples = unique_triples

        # 4. ADD PROVENANCE
        triples_with_provenance = self._add_provenance(
            enriched_triples, source, metadata
        )

        # 5. BATCH STORE
        if triples_with_provenance:
            stored_count = self._batch_store(triples_with_provenance, tenant_id=tenant_id)
            stats["stored"] = stored_count

        return stats

    def _validate(self, triples: List[Tuple], stats: Dict) -> List[Tuple]:
        """Validate triples against ontology"""
        validated = []

        for triple in triples:
            try:
                # Convert to list format for validator
                triple_list = list(triple)
                is_valid, error = self.validator.validate_triple(triple_list)

                if is_valid:
                    validated.append(triple)
                    stats["validated"] += 1
                else:
                    stats["errors"].append(f"Validation failed for {triple}: {error}")
            except Exception as e:
                stats["errors"].append(f"Validation error for {triple}: {e}")

        return validated

    def _deduplicate(self, triples: List[Tuple], stats: Dict) -> List[Tuple]:
        """Remove duplicate triples"""
        unique = []

        for triple in triples:
            # Create hash of triple
            triple_hash = hashlib.md5(
                f"{triple[0]}|{triple[1]}|{triple[2]}".encode()
            ).hexdigest()

            if triple_hash not in self.seen_hashes:
                self.seen_hashes.add(triple_hash)
                unique.append(triple)
            else:
                stats["duplicates"] += 1

        return unique

    def _enrich(self, triples: List[Tuple], stats: Dict) -> List[Tuple]:
        """Apply OWL reasoning to infer new triples"""
        enriched = list(triples)  # Start with original

        try:
            # Add triples to reasoner's graph temporarily
            for s, p, o in triples:
                # Simple inference: if we have (X, isA, Y), we might infer more
                pass  # Placeholder - actual reasoning happens in OWLReasoningAgent

            # For now, just return original triples
            # TODO: Integrate OWL reasoning for automatic inference
            stats["enriched"] = 0

        except Exception as e:
            stats["errors"].append(f"Enrichment error: {e}")

        return enriched

    def _add_provenance(self,
                        triples: List[Tuple],
                        source: str,
                        metadata: Optional[Dict] = None) -> List[Dict]:
        """Add provenance metadata to each triple"""
        timestamped = []

        for triple in triples:
            triple_with_meta = {
                "subject": triple[0],
                "predicate": triple[1],
                "object": triple[2],
                "provenance": {
                    "source": source,
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": metadata.get("method", "SLM") if metadata else "SLM"
                }
            }

            if metadata:
                triple_with_meta["provenance"].update(metadata)

            timestamped.append(triple_with_meta)

        return timestamped

    def _batch_store(self, triples_with_meta: List[Dict], tenant_id: str = "default") -> int:
        """Store triples in Rust backend efficiently"""
        try:
            # Convert back to simple tuples for Rust client
            simple_triples = [
                (t["subject"], t["predicate"], t["object"])
                for t in triples_with_meta
            ]

            # TODO: Store provenance metadata separately
            # For now, just store the triples
            if self.rust_client.connected:
                result = self.rust_client.ingest_triples(simple_triples, tenant_id=tenant_id)
                return len(simple_triples) # Or check result['edges_added']
            return 0
        except Exception as e:
            print(f"❌ Batch storage error: {e}")
            return 0

    def clear_dedup_cache(self):
        """Clear deduplication cache (useful for testing)"""
        self.seen_hashes.clear()
