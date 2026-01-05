"""
Motor de Inferencia OWL/RDFS ligero.
Expande el grafo de conocimiento aplicando reglas lógicas básicas.
"""
from typing import List, Set, Tuple
import rdflib
from rdflib import RDF, RDFS, OWL, URIRef

class InferenceEngine:
    def __init__(self, ontology_graph: rdflib.Graph):
        self.ontology = ontology_graph
        self.cache_subclasses = {}
        self.cache_subproperties = {}
        self._precompute_hierarchy()

    def _precompute_hierarchy(self):
        """Pre-computar jerarquías para inferencia rápida"""
        # Subclases
        for s, p, o in self.ontology.triples((None, RDFS.subClassOf, None)):
            if s not in self.cache_subclasses:
                self.cache_subclasses[s] = set()
            self.cache_subclasses[s].add(o)

        # Subpropiedades
        for s, p, o in self.ontology.triples((None, RDFS.subPropertyOf, None)):
            if s not in self.cache_subproperties:
                self.cache_subproperties[s] = set()
            self.cache_subproperties[s].add(o)

    def expand_triples(self, triples: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """
        Aplica reglas de inferencia a una lista de triples.
        Devuelve los triples originales + los inferidos.
        """
        expanded = set(triples)
        new_triples = set(triples)

        while new_triples:
            current_triple = new_triples.pop()
            s, p, o = current_triple

            # Regla 1: Herencia de Tipos (Si X es Perro, X es Animal)
            # (s, rdf:type, C) AND (C rdfs:subClassOf D) => (s, rdf:type, D)
            is_type_predicate = (
                p == "isA" or
                p == "rdf:type" or
                p == str(RDF.type) or
                p == RDF.type
            )

            if is_type_predicate:
                # Buscar superclases de 'o'
                # Nota: Esto requiere que 'o' sea una URI válida en la ontología
                # Aquí hacemos una búsqueda aproximada o directa si es URI
                super_classes = self._get_superclasses(o)
                for super_class in super_classes:
                    inferred = (s, p, super_class)
                    if inferred not in expanded:
                        expanded.add(inferred)
                        new_triples.add(inferred)

            # Regla 2: Jerarquía de Propiedades
            # (s, P, o) AND (P rdfs:subPropertyOf Q) => (s, Q, o)
            super_props = self._get_superproperties(p)
            for super_prop in super_props:
                inferred = (s, super_prop, o)
                if inferred not in expanded:
                    expanded.add(inferred)
                    new_triples.add(inferred)

            # Regla 3: Dominios y Rangos (Inferencia de Tipos)
            # (s, P, o) AND (P rdfs:domain C) => (s, rdf:type, C)
            # (s, P, o) AND (P rdfs:range C) => (o, rdf:type, C)
            # TODO: Implementar si tenemos metadatos de dominio/rango cargados

        return list(expanded)

    def _get_superclasses(self, concept: str) -> Set[str]:
        """Devuelve todas las superclases (transitivo)"""
        from rdflib import URIRef

        # Convertir string a URIRef si es necesario
        if isinstance(concept, str):
            if concept.startswith("http"):
                concept_uri = URIRef(concept)
            else:
                # Buscar URI que termine con este concepto
                matches = self._resolve_concept_to_uri(concept)
                if not matches:
                    return set()
                concept_uri = matches[0]
        else:
            concept_uri = concept

        super_classes = set()

        # BFS para transitividad
        queue = [concept_uri]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            # Buscar superclases directas en el grafo
            for s, p, o in self.ontology.triples((current, RDFS.subClassOf, None)):
                super_class_str = self._uri_to_string(o)
                super_classes.add(super_class_str)
                queue.append(o)

        return super_classes

    def _get_superproperties(self, prop: str) -> Set[str]:
        uris = self._resolve_concept_to_uri(prop)
        super_props = set()
        for uri in uris:
            if uri in self.cache_subproperties:
                for p in self.cache_subproperties[uri]:
                    super_props.add(self._uri_to_string(p))
        return super_props

    def _resolve_concept_to_uri(self, concept: str) -> List[URIRef]:
        """Intenta encontrar la URI completa para un string corto"""
        # Búsqueda ingenua en el grafo
        matches = []
        # 1. Probar si es URI completa
        if concept.startswith("http"):
            return [URIRef(concept)]

        # 2. Buscar por fragmento
        for s in self.ontology.subjects():
            if isinstance(s, URIRef) and s.split('#')[-1] == concept:
                matches.append(s)
        return matches

    def _uri_to_string(self, uri: URIRef) -> str:
        return uri.split('#')[-1]
