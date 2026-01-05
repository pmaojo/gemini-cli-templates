"""
Cypher Query Executor for Triple Graph
Executes Cypher queries on the Rust-stored knowledge graph
"""
from typing import List, Dict, Any, Tuple
from agents.infrastructure.web.client import get_client

class CypherExecutor:
    """
    Executes Cypher queries on the triple-based knowledge graph.

    Translates Cypher to graph traversal operations on the Rust backend.
    """

    def __init__(self):
        self.rust_client = get_client()

    def execute(self, cypher: str) -> Dict[str, Any]:
        """
        Execute a Cypher query.

        Args:
            cypher: Cypher query string

        Returns:
            Query results with nodes and relationships
        """
        if not self.rust_client.connected:
            return {"error": "Rust backend not connected"}

        # Parse Cypher query
        parsed = self._parse_cypher(cypher)

        if "error" in parsed:
            return parsed

        # Execute on Rust backend
        results = self._execute_on_rust(parsed)

        return results

    def _parse_cypher(self, cypher: str) -> Dict[str, Any]:
        """
        Simple Cypher parser for basic MATCH...RETURN queries.

        Supports:
        - MATCH (n)-[:predicate]->(m) WHERE ... RETURN ...
        - MATCH (n) WHERE n = 'value' RETURN n
        """
        cypher_upper = cypher.upper()

        if "MATCH" not in cypher_upper or "RETURN" not in cypher_upper:
            return {"error": "Query must contain MATCH and RETURN"}

        # Extract MATCH pattern
        match_start = cypher_upper.index("MATCH") + 5

        # Find WHERE or RETURN
        where_idx = cypher_upper.find("WHERE", match_start)
        return_idx = cypher_upper.index("RETURN")

        if where_idx > 0:
            pattern = cypher[match_start:where_idx].strip()
            where_clause = cypher[where_idx + 5:return_idx].strip()
        else:
            pattern = cypher[match_start:return_idx].strip()
            where_clause = None

        return_clause = cypher[return_idx + 6:].strip()

        return {
            "pattern": pattern,
            "where": where_clause,
            "return": return_clause
        }

    def _execute_on_rust(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute parsed query on Rust backend.

        Since Rust backend doesn't have native Cypher support,
        we translate to graph operations.
        """
        # Get all triples from Rust
        all_triples = self.rust_client.get_all_triples()

        if not all_triples:
            return {"results": [], "count": 0}

        # Filter triples based on WHERE clause
        filtered = self._filter_triples(all_triples, parsed.get("where"))

        # Format results
        results = []
        for s, p, o in filtered[:20]:  # Limit to 20 results
            results.append({
                "subject": s,
                "predicate": p,
                "object": o
            })

        return {
            "results": results,
            "count": len(results),
            "total_matches": len(filtered)
        }

    def _filter_triples(self, triples: List[Tuple[str, str, str]], where_clause: str) -> List[Tuple]:
        """Filter triples based on WHERE clause"""
        if not where_clause:
            return triples

        filtered = []
        where_lower = where_clause.lower()

        for s, p, o in triples:
            # Simple filtering logic
            match = True

            # Check for CONTAINS
            if "contains" in where_lower:
                # Extract: "s CONTAINS 'Swale'"
                parts = where_clause.split("CONTAINS")
                if len(parts) >= 2:
                    value = parts[1].strip().strip("'\"")
                    if value.lower() not in s.lower() and value.lower() not in o.lower():
                        match = False

            # Check for equality: "n = 'value'"
            if "=" in where_clause and ">" not in where_clause and "<" not in where_clause:
                parts = where_clause.split("=")
                if len(parts) >= 2:
                    value = parts[1].strip().strip("'\"")
                    if value != s and value != o:
                        match = False

            # Check for AND conditions
            if " and " in where_lower:
                conditions = where_clause.split(" AND ")
                for cond in conditions:
                    if "contains" in cond.lower():
                        value = cond.split("CONTAINS")[1].strip().strip("'\"")
                        if value.lower() not in s.lower() and value.lower() not in o.lower() and value.lower() not in p.lower():
                            match = False

            if match:
                filtered.append((s, p, o))

        return filtered

    def format_results_as_text(self, results: Dict[str, Any]) -> str:
        """Format query results as human-readable text"""
        if "error" in results:
            return f"❌ Error: {results['error']}"

        count = results.get("count", 0)
        if count == 0:
            return "No results found."

        text = f"Found {results['count']} results"
        if results["total_matches"] > results["count"]:
            text += f" (showing first {results['count']} of {results['total_matches']})"
        text += ":\n\n"

        for i, r in enumerate(results["results"], 1):
            text += f"{i}. **{r['subject']}** --[{r['predicate']}]--> **{r['object']}**\n"

        return text
