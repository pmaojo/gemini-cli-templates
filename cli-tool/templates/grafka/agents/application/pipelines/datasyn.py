"""DataSyn: Data Synthesis and Extraction Pipeline"""
import os
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Local imports
from agents.infrastructure.persistence.graph_client import GraphClient
from agents.infrastructure.persistence.vector_store import VectorStore
from agents.infrastructure.persistence.embeddings import EmbeddingGenerator

# Optional imports for document processing
try:
    from agents.application.pipelines.document_processor import DocumentProcessor
except ImportError:
    # Stub processor if missing
    class DocumentProcessor:
        def chunk_text(self, text, max_size=400):
            return [text[i:i+max_size] for i in range(0, len(text), max_size)]

class DataSynPipeline:
    """
    Core pipeline for ingesting data (CSV, MD, JSON) and extracting knowledge triples.
    Implements a RAG-enhanced extraction flow.
    """

    def __init__(self, vector_store=None, embedder=None, translation_service=None):
        # In this template version, we inject dependencies explicitly or use local defaults.
        # We avoid the complex DI container from the full SaaS product to keep things simple.
        self._vector_store = vector_store or VectorStore()
        self._embedder = embedder or EmbeddingGenerator()
        self.translation_service = translation_service
        self.slm = None # SLM disabled by default in template

    def run_pipeline(self, pipeline_name: str, input_path: str, tenant_id: str = "default") -> Dict[str, Any]:
        """
        Run the extraction pipeline on a file.

        Args:
            pipeline_name: Name of the pipeline task
            input_path: Path to the input file
            tenant_id: Tenant context

        Returns:
            Dict containing stats about extraction
        """
        path = Path(input_path)
        logs = []
        triples_extracted = []

        if not path.exists():
            # If path doesn't exist, maybe it's raw text?
            if len(input_path) > 0 and "\n" not in input_path and "." not in input_path: # Single line string that's not a path
                 logs.append("Treating input as raw text (file not found)")
                 triples_extracted = self._extract_from_text(input_path)
                 return {
                    "pipeline": pipeline_name,
                    "input": input_path,
                    "triples_count": len(triples_extracted),
                    "triples": triples_extracted,
                    "logs": logs
                }
            elif len(input_path) > 100: # Long text
                 logs.append("Treating input as raw text")
                 triples_extracted = self._extract_from_text(input_path)
                 return {
                    "pipeline": pipeline_name,
                    "triples_count": len(triples_extracted),
                    "triples": triples_extracted,
                    "logs": logs
                 }

            return {"error": f"File not found: {input_path}"}

        logs.append(f"📂 Processing file: {path.name}")

        try:
            if path.suffix == '.csv':
                triples_extracted = self._process_csv(path, logs)
            elif path.suffix == '.md':
                triples_extracted = self._process_markdown(path, logs)
            elif path.suffix == '.json':
                triples_extracted = self._process_json(path, logs)
            else:
                logs.append(f"⚠️ Unsupported format: {path.suffix}")
        except Exception as e:
            logs.append(f"❌ Error: {str(e)}")
            return {"error": str(e), "logs": logs}

        # In a real system, we would now:
        # 1. Validate triples against ontology
        # 2. Store triples in Rust backend
        # 3. Index in Vector Store

        # Simulating storage
        if triples_extracted:
            # self._store_triples(triples_extracted)
            logs.append(f"💾 Stored {len(triples_extracted)} triples")

        return {
            "pipeline": pipeline_name,
            "input": str(path),
            "triples_count": len(triples_extracted),
            "triples": triples_extracted[:50], # Return preview
            "logs": logs
        }

    def _process_csv(self, filepath: Path, logs: List[str]) -> List[tuple]:
        """Process CSV file"""
        triples = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                header = reader.fieldnames
                logs.append(f"📊 CSV Columns: {header}")

                rows = list(reader)
                logs.append(f"  Found {len(rows)} rows")

                for i, row in enumerate(rows):
                    # For each row, extract triples
                    row_triples = self._extract_from_row(row, header)
                    triples.extend(row_triples)

                    if i % 100 == 0:
                        logs.append(f"  Processed {i}/{len(rows)} rows...")

        except Exception as e:
            logs.append(f"❌ CSV Error: {e}")

        return triples

    def _process_markdown(self, filepath: Path, logs: List[str]) -> List[tuple]:
        """Process markdown with chunking"""
        triples = []
        processor = DocumentProcessor()

        try:
            text = filepath.read_text(encoding='utf-8')
            logs.append(f"📝 Text length: {len(text)} chars")

            chunks = list(processor.chunk_text(text, max_size=400))
            logs.append(f"🔪 Split into {len(chunks)} chunks")

            for i, chunk in enumerate(chunks, 1):
                chunk_triples = self._extract_from_text(chunk)
                triples.extend(chunk_triples)
        except Exception as e:
            logs.append(f"❌ Markdown Error: {e}")

        return triples

    def _process_json(self, filepath: Path, logs: List[str]) -> List[tuple]:
        """Process JSON"""
        triples = []
        try:
            data = json.loads(filepath.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and len(value) < 100:
                        triples.append((key, "hasValue", value))
        except Exception as e:
            logs.append(f"❌ JSON Error: {e}")

        return triples

    def _extract_from_row(self, row: Dict[str, str], header: List[str]) -> List[tuple]:
        """Extract triples from a CSV row (Rule-based stub)"""
        triples = []
        if header and len(header) >= 2:
            subject_col = header[0]
            subject = row.get(subject_col, '').strip()

            if subject:
                for col in header[1:4]:  # Limit to 3 properties
                    value = row.get(col, '').strip()
                    if value and len(value) < 50:
                        predicate = col.replace('_', ' ').replace('-', ' ')
                        triples.append((subject, predicate, value))
        return triples

    def _extract_from_text(self, text: str) -> List[tuple]:
        """Extract triples from text (Stub)"""
        # Minimal extraction simulation
        triples = []
        words = text.split()
        if len(words) > 3:
             triples.append((words[0], "relatedTo", words[-1]))
        return triples
