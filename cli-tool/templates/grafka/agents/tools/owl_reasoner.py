"""
OWL Reasoning Agent - Automated Knowledge Inference
Optimized with Agent Lightning's AIR system
"""
from typing import List, Tuple, Dict, Set
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from agents.infrastructure.ai.air import get_air, RewardSignal

class OWLReasoningAgent:
    """
    Applies OWL inference rules to expand knowledge graph.
    Uses Agent Lightning optimization to learn which rules are most valuable.
    """

    def __init__(self, ontology_graph: Graph):
        self.ontology = ontology_graph
        self.air = get_air()

        # Define inference rules
        self.rules = {
            "subclass_transitivity": self._infer_subclass,
            "type_propagation": self._infer_type_propagation,  # NEW: Instance reasoning
            "transitive_properties": self._infer_transitive,
            "inverse_properties": self._infer_inverse,
            "domain_range": self._infer_domain_range,  # NEW: Property constraints
            "symmetric_properties": self._infer_symmetric
        }

    def infer(self, triples: List[Tuple[str, str, str]],
              rules: List[str] = None) -> Dict[str, any]:
        """
        Apply OWL reasoning to infer new triples.

        Args:
            triples: Input triples (subject, predicate, object)
            rules: Which rules to apply (default: all)

        Returns:
            {
                "original_count": int,
                "inferred_triples": List[Tuple],
                "total_count": int,
                "expansion_ratio": float,
                "rules_applied": Dict[str, int]
            }
        """
        self.air.reset()

        if rules is None:
            rules = list(self.rules.keys())

        # Convert triples to RDF graph
        temp_graph = Graph()
        SYS = Namespace("http://sys.semantic/")

        for s, p, o in triples:
            # Resolve URIs if possible
            s_uri = self._resolve_single_uri(s, SYS)
            p_uri = self._resolve_single_uri(p, SYS)
            o_uri = self._resolve_single_uri(o, SYS)

            temp_graph.add((s_uri, p_uri, o_uri))

        # Apply each rule
        inferred = set()
        rules_applied = {}

        for rule_name in rules:
            if rule_name in self.rules:
                rule_func = self.rules[rule_name]
                new_triples = rule_func(temp_graph, SYS)

                # Track new inferences
                before = len(inferred)
                inferred.update(new_triples)
                after = len(inferred)

                count = after - before
                rules_applied[rule_name] = count

                # AIR: Reward for new inferences
                if count > 0:
                    self.air.record_event(
                        RewardSignal.OWL_CONSISTENT,
                        {"rule": rule_name, "inferences": count}
                    )

        # Convert back to simple triples
        inferred_list = []
        for s, p, o in inferred:
            s_str = str(s).split('/')[-1]
            p_str = str(p).split('/')[-1]
            o_str = str(o).split('/')[-1]
            inferred_list.append((s_str, p_str, o_str))

        # Calculate metrics
        original_count = len(triples)
        total_count = original_count + len(inferred_list)
        expansion_ratio = total_count / original_count if original_count > 0 else 0

        return {
            "original_count": original_count,
            "inferred_triples": inferred_list,
            "total_count": total_count,
            "expansion_ratio": expansion_ratio,
            "rules_applied": rules_applied,
            "air_summary": self.air.get_summary()
        }

    def _resolve_single_uri(self, concept: str, default_ns: Namespace):
        """Helper to resolve a string to a URI"""
        from rdflib import URIRef

        # 1. Check if it's a full URI
        if concept.startswith("http"):
            return URIRef(concept)

        # 2. Check if it's a CURIE (e.g., rdf:type)
        if ":" in concept:
            prefix, local = concept.split(":", 1)
            if prefix == "rdf": return RDF[local]
            if prefix == "rdfs": return RDFS[local]
            if prefix == "owl": return OWL[local]

        # 3. Try agriculture namespace first (most common)
        AGR = Namespace("http://sys.semantic/agriculture#")
        agr_uri = AGR[concept]
        if (agr_uri, None, None) in self.ontology or (None, None, agr_uri) in self.ontology:
            print(f"  ✓ Resolved '{concept}' → agriculture:{concept}")
            return agr_uri

        # 4. Try to find in ontology by fragment
        matches = self._resolve_concept_to_uri(concept)
        if matches:
            print(f"  ✓ Resolved '{concept}' → {matches[0]}")
            return matches[0]

        # 5. Fallback to default namespace
        print(f"  ⚠️ '{concept}' not in ontology, using default namespace")
        return default_ns[concept]

    def _resolve_concept_to_uri(self, concept: str) -> List[any]:
        """Try to find full URI for a short string"""
        from rdflib import URIRef

        matches = []
        # 1. Check if full URI
        if concept.startswith("http"):
            return [URIRef(concept)]

        # 2. Search by fragment
        for s in self.ontology.subjects():
            if isinstance(s, URIRef) and str(s).split('#')[-1] == concept:
                matches.append(s)
        return matches

    def _infer_subclass(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply rdfs:subClassOf transitivity.
        If A subClassOf B and B subClassOf C, then A subClassOf C
        """
        inferred = set()

        # Query for subclass relationships
        query = """
        SELECT ?a ?c WHERE {
            ?a rdfs:subClassOf ?b .
            ?b rdfs:subClassOf ?c .
            FILTER (?a != ?c)
        }
        """

        for row in graph.query(query):
            inferred.add((row.a, RDFS.subClassOf, row.c))

        return inferred

    def _infer_type_propagation(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply instance-level type propagation (CRITICAL for reasoning).
        If X rdf:type A and A rdfs:subClassOf B, then X rdf:type B

        Scientific basis: RDFS semantics - transitive class membership
        This is the KEY missing piece for meaningful OWL reasoning!
        """
        inferred = set()

        # Find all instances and their types
        for instance, _, class_a in graph.triples((None, RDF.type, None)):
            # Find all superclasses of class_a
            superclasses = set()
            self._collect_superclasses(class_a, superclasses)

            # Infer that instance is also of type superclass
            for superclass in superclasses:
                if (instance, RDF.type, superclass) not in graph:
                    inferred.add((instance, RDF.type, superclass))

        return inferred

    def _collect_superclasses(self, cls, collected: set):
        """Recursively collect all superclasses (transitive closure)"""
        for _, _, superclass in self.ontology.triples((cls, RDFS.subClassOf, None)):
            if superclass not in collected:
                collected.add(superclass)
                self._collect_superclasses(superclass, collected)


    def _infer_transitive(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply transitivity for properties marked as owl:TransitiveProperty.
        If (A, P, B) and (B, P, C) and P is transitive, then (A, P, C)
        """
        inferred = set()

        # Find transitive properties in ontology
        transitive_props = set()
        for prop in self.ontology.subjects(RDF.type, OWL.TransitiveProperty):
            transitive_props.add(prop)

        # Apply transitivity
        for prop in transitive_props:
            # Find chains
            for s, p, o in graph.triples((None, prop, None)):
                for s2, p2, o2 in graph.triples((o, prop, None)):
                    if s != o2:
                        inferred.add((s, prop, o2))

        return inferred

    def _infer_inverse(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply owl:inverseOf.
        If (A, P, B) and P inverseOf Q, then (B, Q, A)
        """
        inferred = set()

        # Find inverse property pairs
        inverse_pairs = {}
        for p1, _, p2 in self.ontology.triples((None, OWL.inverseOf, None)):
            inverse_pairs[p1] = p2
            inverse_pairs[p2] = p1

        # Apply inverses
        for s, p, o in graph:
            if p in inverse_pairs:
                inverse_p = inverse_pairs[p]
                inferred.add((o, inverse_p, s))

        return inferred

    def _infer_symmetric(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply owl:SymmetricProperty.
        If (A, P, B) and P is symmetric, then (B, P, A)
        """
        inferred = set()

        # Find symmetric properties in ontology
        symmetric_props = set()
        for prop in self.ontology.subjects(RDF.type, OWL.SymmetricProperty):
            symmetric_props.add(prop)

        # Apply symmetry
        for prop in symmetric_props:
            for s, p, o in graph.triples((None, prop, None)):
                if (o, prop, s) not in graph:
                    inferred.add((o, prop, s))

        return inferred

    def _infer_domain_range(self, graph: Graph, ns: Namespace) -> Set[Tuple]:
        """
        Apply rdfs:domain and rdfs:range constraints.
        If (X, P, Y) and P has domain D, then X rdf:type D
        If (X, P, Y) and P has range R, then Y rdf:type R

        Scientific basis: RDFS property constraints
        """
        inferred = set()

        # Collect domain and range constraints from ontology
        domains = {}
        ranges = {}
        for prop, _, domain in self.ontology.triples((None, RDFS.domain, None)):
            domains[prop] = domain
        for prop, _, range_class in self.ontology.triples((None, RDFS.range, None)):
            ranges[prop] = range_class

        # Apply constraints to graph triples
        for s, p, o in graph.triples((None, None, None)):
            # Apply domain constraint
            if p in domains:
                if (s, RDF.type, domains[p]) not in graph:
                    inferred.add((s, RDF.type, domains[p]))

            # Apply range constraint
            if p in ranges:
                if (o, RDF.type, ranges[p]) not in graph:
                    inferred.add((o, RDF.type, ranges[p]))

        return inferred

    def format_results(self, result: Dict) -> str:
        """Format inference results as human-readable text"""
        text = f"**OWL Reasoning Results**\n\n"
        text += f"📊 Original: {result['original_count']} triples\n"
        text += f"✨ Inferred: {len(result['inferred_triples'])} new triples\n"
        text += f"📈 Total: {result['total_count']} triples\n"
        text += f"🚀 Expansion: {result['expansion_ratio']:.1%}\n\n"

        if result['rules_applied']:
            text += "**Rules Applied:**\n"
            for rule, count in result['rules_applied'].items():
                if count > 0:
                    text += f"- {rule}: {count} inferences\n"

        if result['inferred_triples']:
            text += "\n**Sample Inferences:**\n"
            for s, p, o in result['inferred_triples'][:5]:
                text += f"- ({s}, {p}, {o})\n"

        text += f"\n{result['air_summary']}"

        return text
