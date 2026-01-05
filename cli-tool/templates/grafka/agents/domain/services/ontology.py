import rdflib
from rdflib import RDF, RDFS, OWL, Namespace
from typing import Set, Dict, Optional, List, Union
import json
import os
import requests
from dataclasses import dataclass, asdict

@dataclass
class OntologySource:
    path: str  # File path or URL
    type: str  # 'file' or 'url'
    format: Optional[str] = None # 'xml', 'turtle', etc. (optional, auto-detect if None)
    enabled: bool = True
    metadata: Dict = None # Name, description, etc.

class OntologyService:
    """
    Service to load and query the OWL ontology for agents.
    Manages multiple ontology sources (files, URLs) with persistence.
    """
    def __init__(self, ontology_files: list[str] = None, persistence_file: str = "ontology_registry.json"):
        self.graph = rdflib.Graph()
        self.sources: List[OntologySource] = []
        self.persistence_file = persistence_file

        # Load from persistence first
        self.load_registry()

        # Add legacy/hardcoded files if not present
        if ontology_files:
            for file_path in ontology_files:
                if not any(s.path == file_path for s in self.sources):
                    self.add_ontology_source(file_path, "file", save=False)

        # Initial Load
        self.reload_graph()

    def add_ontology_source(self, path: str, type: str, format: str = None, metadata: Dict = None, save: bool = True):
        """Add a new ontology source."""
        # Check if already exists
        for source in self.sources:
            if source.path == path:
                # Update enabled state if re-added
                source.enabled = True
                if metadata:
                    source.metadata = metadata
                if save:
                    self.save_registry()
                return

        new_source = OntologySource(path=path, type=type, format=format, metadata=metadata or {})
        self.sources.append(new_source)
        if save:
            self.save_registry()

    def remove_ontology_source(self, path: str):
        """Remove a source permanently."""
        self.sources = [s for s in self.sources if s.path != path]
        self.save_registry()

    def toggle_ontology_source(self, path: str, enabled: bool):
        """Enable/Disable a source."""
        for source in self.sources:
            if source.path == path:
                source.enabled = enabled
        self.save_registry()

    def load_registry(self):
        """Load sources from JSON file."""
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    data = json.load(f)
                    self.sources = [OntologySource(**item) for item in data]
            except Exception as e:
                print(f"Error loading ontology registry: {e}")

    def save_registry(self):
        """Save sources to JSON file."""
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump([asdict(s) for s in self.sources], f, indent=2)
        except Exception as e:
            print(f"Error saving ontology registry: {e}")

    def reload_graph(self):
        """Reloads the graph from all enabled sources."""
        self.graph = rdflib.Graph()
        loaded_count = 0

        for source in self.sources:
            if not source.enabled:
                continue

            print(f"Loading ontology: {source.path} ({source.type})...")
            try:
                if source.type == 'url':
                    # Try direct load first, fallback to requests
                    try:
                        self.graph.parse(source.path, format=source.format)
                    except Exception as e:
                        print(f"  Direct load failed, trying requests... ({e})")
                        response = requests.get(source.path)
                        response.raise_for_status()
                        self.graph.parse(data=response.text, format=source.format or rdflib.util.guess_format(source.path) or 'xml')
                else:
                    # File
                    self.graph.parse(source.path, format=source.format)

                loaded_count += 1
            except Exception as e:
                print(f"❌ Error loading ontology {source.path}: {e}")

        print(f"✅ Loaded {loaded_count} ontologies. Total triples: {len(self.graph)}")
        self.classes = self._extract_classes()
        self.properties = self._extract_properties()

    def get_stats(self):
        """Return simple stats about loaded ontologies"""
        return {
            "sources": len(self.sources),
            "enabled": len([s for s in self.sources if s.enabled]),
            "triples": len(self.graph),
            "classes": len(self.classes),
            "properties": len(self.properties)
        }

    def _extract_classes(self) -> Set[str]:
        classes = set()
        for s, p, o in self.graph.triples((None, RDF.type, OWL.Class)):
            classes.add(str(s))
        return classes

    def _extract_properties(self) -> Set[str]:
        props = set()
        for s, p, o in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            props.add(str(s))
        for s, p, o in self.graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            props.add(str(s))
        return props

    def is_valid_class(self, uri: str) -> bool:
        return uri in self.classes

    def is_valid_property(self, uri: str) -> bool:
        return uri in self.properties

    def fuzzy_match_class(self, term: str) -> Optional[str]:
        """
        Simple fuzzy matcher to find the closest class URI for a given term.
        In a real system, use embeddings or Levenshtein distance.
        """
        term_lower = term.lower()
        best_match = None

        # Check labels first
        for s, p, o in self.graph.triples((None, RDFS.label, None)):
            if str(o).lower() == term_lower:
                return str(s)

        # Check local names
        for cls in self.classes:
            if cls.split('#')[-1].lower() == term_lower:
                return cls

        return None
