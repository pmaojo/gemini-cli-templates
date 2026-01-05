"""
Enhanced CSV Processor with RAG-based Context Extraction
Instead of line-by-line extraction, uses document RAG to understand context
"""
from typing import List, Tuple, Dict, Any
from pathlib import Path
import csv

class RAGEnhancedCSVProcessor:
    """
    Process CSV files using RAG to understand document context.

    Workflow:
    1. Load entire CSV into memory
    2. Create document embeddings for semantic search
    3. For each row, use RAG to find related context
    4. Extract triples with full context awareness
    """

    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store
        self.document_context = {}

    def process_csv(self, filepath: Path, tenant_id: str = None) -> List[Tuple[str, str, str]]:
        """
        Process CSV with RAG-based context extraction.

        Args:
            filepath: Path to CSV file
            tenant_id: Tenant ID for isolation

        Returns:
            List of extracted triples
        """
        # Step 1: Load and index entire document
        rows = self._load_csv(filepath)

        if not rows:
            return []

        # Step 2: Build document context via RAG
        self._build_document_context(rows, filepath.stem, tenant_id)

        # Step 3: Extract triples with context
        triples = []
        for i, row in enumerate(rows):
            # Get contextual information via RAG
            context = self._get_row_context(row, i, rows, tenant_id)

            # Extract triples using context
            row_triples = self._extract_with_context(row, context)
            triples.extend(row_triples)

        return triples

    def _load_csv(self, filepath: Path) -> List[Dict[str, str]]:
        """Load CSV into memory"""
        rows = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []

        return rows

    def _build_document_context(self, rows: List[Dict], doc_name: str, tenant_id: str = None):
        """
        Build document-level context using embeddings.
        Index each row for semantic search.
        """
        for i, row in enumerate(rows):
            # Create rich description of row
            row_text = " | ".join([f"{k}: {v}" for k, v in row.items() if v])

            # Generate embedding
            embedding = self.embedder.encode_single(row_text)

            # Store in vector store with metadata
            self.vector_store.add(
                node_id=f"{doc_name}_row_{i}",
                vector=embedding,
                metadata={
                    "row_index": i,
                    "row_data": row,
                    "document": doc_name,
                    "description": row_text[:200]
                },
                tenant_id=tenant_id
            )

    def _get_row_context(self, row: Dict, row_index: int, all_rows: List[Dict], tenant_id: str = None) -> Dict[str, Any]:
        """
        Get contextual information for a row using RAG.

        Returns:
            {
                "similar_rows": List of semantically similar rows,
                "previous_rows": Nearby rows for sequential context,
                "column_patterns": Patterns detected in columns
            }
        """
        # Create query from current row
        query_text = " ".join([str(v) for v in row.values() if v])
        query_emb = self.embedder.encode_single(query_text)

        # Find similar rows via RAG
        similar = self.vector_store.search(query_emb, top_k=3, tenant_id=tenant_id)

        # Get sequential context (previous/next rows)
        previous_rows = []
        if row_index > 0:
            previous_rows.append(all_rows[row_index - 1])
        if row_index > 1:
            previous_rows.append(all_rows[row_index - 2])

        # Analyze column patterns
        column_patterns = self._analyze_columns(row, all_rows)

        return {
            "similar_rows": [r.metadata for r in similar],
            "previous_rows": previous_rows,
            "column_patterns": column_patterns,
            "total_rows": len(all_rows),
            "position": row_index / len(all_rows) if all_rows else 0
        }

    def _analyze_columns(self, row: Dict, all_rows: List[Dict]) -> Dict[str, Any]:
        """Analyze column patterns across the document"""
        patterns = {}

        for col_name, col_value in row.items():
            if not col_value:
                continue

            # Check if column is numeric
            try:
                float(col_value)
                patterns[col_name] = {"type": "numeric", "value": col_value}
            except:
                patterns[col_name] = {"type": "text", "value": col_value}

            # Check if column appears to be a category
            unique_values = set(r.get(col_name, "") for r in all_rows[:100])
            if len(unique_values) < 20:
                patterns[col_name]["is_category"] = True
                patterns[col_name]["categories"] = list(unique_values)[:5]

        return patterns

    def _extract_with_context(self, row: Dict, context: Dict) -> List[Tuple[str, str, str]]:
        """
        Extract triples using full document context.

        Uses:
        - Similar rows to understand relationships
        - Previous rows for sequential patterns
        - Column patterns for type inference
        """
        triples = []

        # Get main entity (usually first column or ID)
        main_entity = None
        for key, value in row.items():
            if value and (key.lower() in ['name', 'id', 'title', 'entity']):
                main_entity = value
                break

        if not main_entity:
            main_entity = list(row.values())[0] if row.values() else "Unknown"

        # Extract relationships based on context
        for col_name, col_value in row.items():
            if not col_value or col_value == main_entity:
                continue

            # Use column patterns to determine relationship type
            col_pattern = context["column_patterns"].get(col_name, {})

            if col_pattern.get("is_category"):
                # Categorical relationship
                predicate = "belongsTo" if "category" in col_name.lower() else "hasProperty"
                triples.append((main_entity, predicate, col_value))

            elif col_pattern.get("type") == "numeric":
                # Numeric property
                predicate = col_name.replace(" ", "_").replace("-", "_")
                triples.append((main_entity, predicate, col_value))

            else:
                # Text relationship - use RAG context to infer
                # Check if similar rows have same pattern
                similar_pattern = self._find_pattern_in_similar(
                    col_name,
                    context["similar_rows"]
                )

                if similar_pattern:
                    triples.append((main_entity, similar_pattern, col_value))
                else:
                    # Default relationship
                    predicate = col_name.replace(" ", "_")
                    triples.append((main_entity, predicate, col_value))

        return triples

    def _find_pattern_in_similar(self, col_name: str, similar_rows: List[Dict]) -> str:
        """Find common pattern in similar rows for this column"""
        # Check if similar rows have this column
        for similar in similar_rows:
            row_data = similar.get("row_data", {})
            if col_name in row_data:
                # Found pattern - use column name as predicate
                return col_name.replace(" ", "_").lower()

        return None
