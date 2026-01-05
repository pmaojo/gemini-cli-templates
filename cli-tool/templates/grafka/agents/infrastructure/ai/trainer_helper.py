"""Helper to format triples from list"""
    def _format_triples_from_list(self, triples):
        """Format list of [s, p, o] as text for the SLM"""
        return "\n".join([f"({t[0]}, {t[1]}, {t[2]})" for t in triples])
