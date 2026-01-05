"""SPARQL query engine for the semantic graph"""
from typing import List, Dict, Any
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

class SPARQLEngine:
    """Execute SPARQL queries against the RDF graph"""

    def __init__(self, ontology_graph: Graph):
        self.graph = ontology_graph

    def query(self, sparql_query: str) -> List[Dict[str, Any]]:
        """Execute a SPARQL query and return results"""
        try:
            results = self.graph.query(sparql_query)
            return [self._row_to_dict(row) for row in results]
        except Exception as e:
            return [{"error": str(e)}]

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SPARQL result row to dictionary"""
        return {str(var): str(val) for var, val in zip(row.labels, row)}

    def get_all_classes(self) -> List[str]:
        """Get all OWL classes"""
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?class ?label WHERE {
            ?class a owl:Class .
            OPTIONAL { ?class rdfs:label ?label }
        }
        """
        return self.query(query)

    def get_all_properties(self) -> List[str]:
        """Get all OWL properties"""
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?prop ?label WHERE {
            { ?prop a owl:ObjectProperty } UNION { ?prop a owl:DatatypeProperty }
            OPTIONAL { ?prop rdfs:label ?label }
        }
        """
        return self.query(query)

    def find_instances_of_class(self, class_uri: str) -> List[str]:
        """Find all instances of a given class"""
        query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?instance WHERE {{
            ?instance rdf:type <{class_uri}> .
        }}
        """
        return self.query(query)
