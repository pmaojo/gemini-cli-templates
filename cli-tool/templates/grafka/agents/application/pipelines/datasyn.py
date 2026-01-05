"""
Document Processing Pipeline
Handles large files with chunking and context-aware processing
"""
import csv
import json
from typing import List, Dict, Any, Iterator, Tuple
from pathlib import Path
from .engine import PipelineStrategy, PipelineResult
from agents.infrastructure.ai.air import get_air, RewardSignal

class DocumentProcessor:
    """Chunks documents intelligently to avoid token limits"""

    MAX_CHUNK_SIZE = 500  # characters per chunk
    OVERLAP = 50  # overlap between chunks for context

    @staticmethod
    def chunk_text(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = OVERLAP) -> Iterator[str]:
        """Split text into overlapping chunks"""
        if len(text) <= max_size:
            yield text
            return

        start = 0
        while start < len(text):
            end = start + max_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, newline, or semicolon
                for char in ['. ', '\n', '; ']:
                    last_break = text[start:end].rfind(char)
                    if last_break > max_size // 2:  # Don't break too early
                        end = start + last_break + len(char)
                        break

            yield text[start:end].strip()
            start = end - overlap

    @staticmethod
    def read_csv_rows(filepath: Path, max_rows: int = 100) -> Iterator[Dict[str, str]]:
        """Read CSV in batches"""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []
            for i, row in enumerate(reader):
                batch.append(row)
                if len(batch) >= max_rows:
                    yield batch
                    batch = []
            if batch:
                yield batch

class DataSynPipeline(PipelineStrategy):
    """
    Process DataSyn files: CSVs, markdown, JSON
    Refactored to use Dependency Injection
    """

    def __init__(self,
                 graph_repo: 'IGraphRepository' = None,
                 embedding_service: 'IEmbeddingService' = None,
                 vector_store: 'IVectorStore' = None,
                 ontology: 'IOntologyService' = None,
                 reasoning: 'IReasoningEngine' = None,
                 slm: Any = None,
                 translation_service: 'ITranslationService' = None):
        """
        Initialize with injected dependencies.
        If None, will use DI container defaults.
        """
        # Use DI container if dependencies not provided
        if any(x is None for x in [graph_repo, embedding_service, vector_store, ontology, reasoning, slm, translation_service]):
            from agents.infrastructure.di_container import get_container
            container = get_container()

            self._graph_repo = graph_repo or container.graph_repository()
            self._embedder = embedding_service or container.embedding_service()
            self._vector_store = vector_store or container.vector_store("grafoso_demo")
            self._ontology = ontology or container.ontology_service()
            self._reasoner = reasoning or container.reasoning_engine()
            self.slm = slm or container.slm() # Assuming SLM is also in container
            self._translation_service = translation_service or container.translation_service()
        else:
            self._graph_repo = graph_repo
            self._embedder = embedding_service
            self._vector_store = vector_store
            self._ontology = ontology
            self._reasoner = reasoning
            self.slm = slm

    @property
    def name(self) -> str:
        return "DataSyn Processor"

    def run(self, input_data: str, **kwargs) -> PipelineResult:
        """
        Args:
            input_data: Filename or path to process
            kwargs: Additional arguments, e.g., tenant_id
        """
        import time
        from agents.infrastructure.web.client import get_client

        # Extract tenant_id from kwargs
        tenant_id = kwargs.get("tenant_id", "default")

        # Initialize AIR for this run
        air = get_air()
        air.reset()

        start_time = time.time()
        logs = []
        all_triples = []

        filepath = Path(input_data)
        if not filepath.exists():
            filepath = Path("documents/DataSyn") / input_data

        if not filepath.exists():
            return PipelineResult(
                success=False,
                data={"error": f"File not found: {input_data}"},
                logs=[f"❌ File not found: {input_data}"],
                execution_time=time.time() - start_time
            )

        logs.append(f"📄 Processing: {filepath.name}")
        logs.append(f"📏 Size: {filepath.stat().st_size / 1024:.1f} KB")
        logs.append(f"👤 Tenant: {tenant_id}")

        # AIR: Reward for successful file access
        air.record_event(RewardSignal.CSV_PARSED, {"file": filepath.name})

        # Route by file type
        if filepath.suffix == '.csv':
            triples = self._process_csv(filepath, logs, tenant_id=tenant_id)
        elif filepath.suffix == '.md':
            triples = self._process_markdown(filepath, logs)
        elif filepath.suffix == '.json':
            triples = self._process_json(filepath, logs)
        else:
            logs.append(f"⚠️ Unsupported file type: {filepath.suffix}")
            triples = []

        all_triples.extend(triples)

        # AIR: Reward for triple extraction
        if triples:
            air.record_event(RewardSignal.TRIPLE_EXTRACTED, {"count": len(triples)})

        # Store in Rust backend
        rust_client = get_client()
        if all_triples and rust_client.connected:
            storage_result = rust_client.ingest_triples(all_triples, tenant_id=tenant_id)
            logs.append(f"💾 Rust Storage: {storage_result.get('edges_added', 0)} edges, {storage_result.get('nodes_added', 0)} nodes")

            # AIR: Reward for successful storage
            air.record_event(RewardSignal.RUST_STORED, {"edges": storage_result.get('edges_added', 0)})

            # Update global graph state
            import sys
            if 'app' in sys.modules:
                # Access the global stored_triples from app.py
                try:
                    import app
                    app.stored_triples.extend(all_triples)
                    logs.append("📊 Updated live graph")
                except:
                    pass

        # Add AIR summary to logs
        logs.append("\n📊 AIR Rewards:")
        logs.append(air.get_summary())

        return PipelineResult(
            success=True,
            data={
                "file": filepath.name,
                "triples_extracted": len(all_triples),
                "triples": [f"({s}, {p}, {o})" for s, p, o in all_triples[:10]],  # Show first 10
                "total_chunks_processed": len(logs) - 2
            },
            logs=logs,
            execution_time=time.time() - start_time
        )



    def _process_csv(self, filepath: Path, logs: List[str], tenant_id: str = "default") -> List[Tuple[str, str, str]]:
        """
        Optimized Incremental CSV Processing + OWL Reasoning
        3. Every 100 rows: Trigger OWL reasoning
        """
        triples = []
        # Use injected dependencies
        embedder = self._embedder
        # Create vector store for this specific CSV (could also be injected/managed)
        from agents.infrastructure.persistence.vector_store import VectorStore
        # We don't need to pass tenant_id here if we pass it in methods, but passing it here sets default for this instance
        vector_store = VectorStore(collection_name=f"csv_{filepath.stem}", dimension=384, tenant_id=tenant_id)
        rust_client = self._graph_repo

        logs.append(f"🔍 Optimized Incremental + OWL: {filepath.name}")

        try:
            import pandas as pd

            # Read CSV with pandas for better error handling
            try:
                df = pd.read_csv(filepath, encoding='utf-8')
            except UnicodeDecodeError:
                # Try different encoding
                df = pd.read_csv(filepath, encoding='latin-1')

            logs.append(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
            logs.append(f"📋 Columns: {', '.join(df.columns.tolist())}")

            for row_num, (idx, row) in enumerate(df.iterrows(), 1):
                try:
                    # Convert row to dict
                    row_dict = row.to_dict()

                    # RAG lookup
                    row_text = " | ".join([f"{k}: {v}" for k, v in row_dict.items() if pd.notna(v)])
                    query_emb = embedder.encode_single(row_text)
                    # Pass tenant_id explicitly to search
                    similar = vector_store.search(query_emb, top_k=3, tenant_id=tenant_id)

                    # Extract with context
                    rag_context = [doc.metadata.get("description", "") for doc in similar]

                    # Use SLM-based extraction (Smart)
                    context_dict = {
                        "similar_rows": rag_context,
                        "header": df.columns.tolist()
                    }

                    row_triples = self._extract_with_rag_context(row_dict, context_dict)

                    if row_triples:
                        logs.append(f"  Row {row_num}: {len(row_triples)} triples")

                        # Store immediately
                        if rust_client.connected:
                            rust_client.ingest_triples(row_triples, tenant_id=tenant_id)
                        triples.extend(row_triples)
                    else:
                        logs.append(f"  Row {row_num}: No triples extracted")

                    # Index for future RAG
                    vector_store.add(
                        node_id=f"{filepath.stem}_row_{row_num}",
                        vector=query_emb,
                        metadata={"description": row_text[:200]},
                        tenant_id=tenant_id
                    )

                except Exception as row_error:
                    logs.append(f"  ❌ Row {row_num} error: {str(row_error)}")
                    continue

                # OWL reasoning every 100 rows
                if row_num % 100 == 0:
                    logs.append(f"  🧠 OWL reasoning at row {row_num}...")
                    try:
                        inferred = self._owl_reasoning(triples[-100:] if len(triples) >= 100 else triples)
                        if inferred:
                            rust_client.ingest_triples(inferred, tenant_id=tenant_id)
                            triples.extend(inferred)
                            logs.append(f"    +{len(inferred)} inferred triples")
                    except Exception as owl_error:
                        logs.append(f"    ⚠️ OWL error: {str(owl_error)}")

                    logs.append(f"  ✓ {row_num} rows, {len(triples)} total triples")

                if row_num >= 1000:
                        logs.append(f"⚠️ Limit reached at {row_num} rows")
                        break

            # Final OWL pass (outside the loop, inside try block)
            logs.append("🧠 Final OWL reasoning...")
            final_inferred = self._owl_reasoning(triples[-100:] if triples else [])
            if final_inferred:
                rust_client.ingest_triples(final_inferred, tenant_id=tenant_id)
                triples.extend(final_inferred)

            logs.append(f"✅ Complete: {len(triples)} triples")
            return triples

        except Exception as e:
            logs.append(f"❌ CSV Processing Error: {str(e)}")
            import traceback
            logs.append(f"Traceback: {traceback.format_exc()}")
            return []  # Return empty list instead of None

    def _extract_optimized(self, row: Dict, rag_context: List[str], header: List[str]) -> List[Tuple[str, str, str]]:
        """Optimized extraction with RAG context"""
        triples = []

        # Main entity
        main_entity = next((v.strip() for v in row.values() if v and v.strip()), None)
        if not main_entity:
            return []

        # Extract with context-aware predicates
        for col_name, col_value in row.items():
            if not col_value or col_value == main_entity:
                continue

            predicate = self._smart_predicate(col_name, rag_context)
            triples.append((main_entity, predicate, col_value.strip()))

        return triples

    def _smart_predicate(self, col_name: str, rag_context: List[str]) -> str:
        """Infer predicate from column + RAG context"""
        col_lower = col_name.lower()

        if "family" in col_lower or "familia" in col_lower:
            return "belongsTo"
        elif "type" in col_lower or "tipo" in col_lower:
            return "isA"
        elif "height" in col_lower or "altura" in col_lower:
            return "hasHeight"
        else:
            return col_name.replace(" ", "_").replace("-", "_")

    def _owl_reasoning(self, recent_triples: List[Tuple]) -> List[Tuple[str, str, str]]:
        """Apply OWL reasoning to recent triples"""
        try:
            from agents.domain.services.ontology import OntologyService
            from agents.tools.owl_reasoner import OWLReasoningAgent

            ontology = OntologyService(["ontology/core.owl", "ontology/agriculture.owl"])
            reasoner = OWLReasoningAgent(ontology.graph)

            result = reasoner.infer(recent_triples)
            return result.get("inferred_triples", [])
        except:
            return []

    def _extract_with_rag_context(self, row: Dict[str, str], context: Dict) -> List[Tuple[str, str, str]]:
        """
        Multi-stage extraction pipeline:

        STAGE 1: RAG to similar rows → Extract initial triples
        STAGE 2: LLM with Cypher → Validate/enrich triples
        STAGE 3: RAG to literature → Extract additional triples

        Args:
            row: Current CSV row
            context: RAG context with similar rows
        """
        triples = []

        # Get main entity (first non-empty value)
        main_entity = None
        for value in row.values():
            if value and value.strip():
                main_entity = value.strip()
                break

        if not main_entity:
            return []

        # LAYER 1: RAG to similar CSV rows (already in context)
        similar_context = "\n".join(context.get("similar_rows", [])[:2])

        # LAYER 2: RAG to ingestion documents
        document_context = self._get_document_context(main_entity)

        # LAYER 3: SLM extraction with full context

        # TRANSLATION STEP (Enforce English for SLM)
        if self.translation_service:
            translated_row = self.translation_service.translate_json(row)
        else:
            translated_row = row # Fallback if service not injected

        row_text = " | ".join([f"{k}: {v}" for k, v in translated_row.items() if v])

        # Build rich prompt for SLM
        extraction_prompt = f"""Extract semantic triples from this CSV row.

CSV Row: {row_text}

Context from similar rows:
{similar_context}

Context from knowledge base:
{document_context}

Extract triples in format: (subject, predicate, object)
Focus on: taxonomic relationships, properties, ecological interactions.
"""

        # Use SLM for extraction (or fallback to rules)
        slm_triples = self._extract_with_slm(extraction_prompt, translated_row, context)

        if slm_triples:
            triples.extend(slm_triples)
        else:
            # Fallback to rule-based extraction
            triples.extend(self._extract_with_rules(row, context))

        return triples

    def _get_document_context(self, entity: str) -> str:
        """
        LAYER 3: RAG search in ingestion documents.
        Search in manual_permacultura, especies.md, etc.
        """
        try:
            # Use global vector store with ingestion docs
            embedder = self._embedder
            # Use injected vector store or create specific one for docs
            doc_store = self._vector_store

            # Search for entity in documents
            query_emb = embedder.encode_single(entity)
            results = doc_store.search(query_emb, top_k=2)

            if results:
                context = "\n".join([r.metadata.get("description", "") for r in results])
                return context[:300]  # Limit context size

        except Exception as e:
            pass

        return "No additional context found"

    def _extract_with_slm(self, prompt: str, row: Dict, context: Dict) -> List[Tuple[str, str, str]]:
        """
        Use SLM (Small Language Model) for extraction.
        Falls back to rules if SLM not available.
        """
        if not self.slm:
            return []

        try:
            # Generate with SLM
            response = self.slm.generate(prompt, max_new_tokens=128)

            # Parse response (expecting JSON list of triples)
            import re
            import json

            triples = []

            # Try to find JSON array in response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    for item in data:
                        if isinstance(item, list) and len(item) == 3:
                            triples.append(tuple(item))
                except:
                    pass

            # Fallback: regex for (s, p, o) format
            if not triples:
                pattern = r'\(([^,]+),\s*([^,]+),\s*([^)]+)\)'
                matches = re.findall(pattern, response)
                for match in matches:
                    triples.append(match)

            return triples

        except Exception as e:
            print(f"SLM extraction failed: {e}")
            return []

    def _extract_with_rules(self, row: Dict[str, str], context: Dict) -> List[Tuple[str, str, str]]:
        """
        Enhanced rule-based extraction using context.
        """
        triples = []

        # Get main entity
        main_entity = None
        for value in row.values():
            if value and value.strip():
                main_entity = value.strip()
                break

        if not main_entity:
            return []

        # Extract relationships with context-aware predicates
        header = context.get("header", [])
        for col_name, col_value in row.items():
            if not col_value or col_value == main_entity:
                continue

            # Use RAG context to infer better predicates
            predicate = self._infer_predicate_from_context(
                col_name,
                col_value,
                context.get("similar_rows", [])
            )

            triples.append((main_entity, predicate, col_value.strip()))

        return triples

    def _infer_predicate_from_context(self, col_name: str, col_value: str, similar_rows: List[str]) -> str:
        """Infer predicate using RAG context"""
        # Check if similar rows mention this column
        col_lower = col_name.lower()

        if "family" in col_lower or "familia" in col_lower:
            return "belongsTo"
        elif "type" in col_lower or "tipo" in col_lower:
            return "isA"
        elif "height" in col_lower or "altura" in col_lower:
            return "hasHeight"
        else:
            # Default: use column name
            return col_name.replace(" ", "_").replace("-", "_")



    def _process_markdown(self, filepath: Path, logs: List[str]) -> List[tuple]:
        """Process markdown with chunking"""
        triples = []
        processor = DocumentProcessor()

        text = filepath.read_text(encoding='utf-8')
        logs.append(f"📝 Text length: {len(text)} chars")

        chunks = list(processor.chunk_text(text, max_size=400))
        logs.append(f"🔪 Split into {len(chunks)} chunks")

        for i, chunk in enumerate(chunks, 1):
            if i % 10 == 0:
                logs.append(f"  Processing chunk {i}/{len(chunks)}...")

            chunk_triples = self._extract_from_text(chunk)
            triples.extend(chunk_triples)

        logs.append(f"✅ Extracted {len(triples)} triples from markdown")
        return triples

    def _process_json(self, filepath: Path, logs: List[str]) -> List[tuple]:
        """Process JSON"""
        triples = []

        data = json.loads(filepath.read_text(encoding='utf-8'))
        logs.append(f"📦 JSON structure: {type(data).__name__}")

        # Simple extraction from JSON keys
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) < 100:
                    triples.append((key, "hasValue", value))

        logs.append(f"✅ Extracted {len(triples)} triples from JSON")
        return triples

    def _extract_from_row(self, row: Dict[str, str], header: List[str]) -> List[tuple]:
        """
        Extract triples from a CSV row.
        Header is included for context (like a prompt template).

        In a real system, this would call:
        LLM/SLM with prompt: "Given CSV with columns: {header}, extract triples from: {row}"
        """
        triples = []

        # Example: if row has 'species' and 'family'
        if 'species' in row and 'family' in row:
            species = row['species'].strip()
            family = row['family'].strip()
            if species and family:
                triples.append((species, "belongsTo", family))

        # Use header to understand column semantics
        # First column is typically the subject/entity
        if header and len(header) >= 2:
            subject_col = header[0]
            subject = row.get(subject_col, '').strip()

            if subject:
                # Extract properties from other columns
                for col in header[1:4]:  # Limit to 3 properties per row
                    value = row.get(col, '').strip()
                    if value and len(value) < 50:  # Skip long values
                        # Use column name as predicate
                        predicate = col.replace('_', ' ').replace('-', ' ')
                        triples.append((subject, predicate, value))

        return triples

    def _extract_from_text(self, text: str) -> List[tuple]:
        """Extract triples from text chunk (simple rule-based)"""
        triples = []
        text_lower = text.lower()

        # Simple pattern matching
        if "plant" in text_lower or "especie" in text_lower:
            if "familia" in text_lower or "family" in text_lower:
                triples.append(("Plant", "hasProperty", "Family"))

        if "suelo" in text_lower or "soil" in text_lower:
            if "nutriente" in text_lower or "nutrient" in text_lower:
                triples.append(("Soil", "contains", "Nutrients"))

        # More sophisticated extraction would use the SLM here
        # For now, keeping it simple to avoid token limits

        return triples
