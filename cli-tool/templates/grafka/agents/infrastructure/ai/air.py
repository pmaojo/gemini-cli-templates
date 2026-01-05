"""
Automatic Intermediate Rewarding (AIR) System
Based on Microsoft's Agent Lightning research

Provides dense feedback for agent training by rewarding intermediate actions
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class RewardSignal(Enum):
    """Types of reward signals"""
    TRIPLE_EXTRACTED = "triple_extracted"
    OWL_CONSISTENT = "owl_consistent"
    RUST_STORED = "rust_stored"
    EMBEDDING_QUALITY = "embedding_quality"
    ONTOLOGY_MAPPED = "ontology_mapped"
    CSV_PARSED = "csv_parsed"
    RAG_RELEVANT = "rag_relevant"
    QUERY_GENERATED = "query_generated"
    QUERY_VALID = "query_valid"
    # User feedback signals (NUEVO - Agent Lightning)
    USER_POSITIVE_FEEDBACK = "user_positive_feedback"
    USER_NEGATIVE_FEEDBACK = "user_negative_feedback"

@dataclass
class RewardEvent:
    """Single reward event"""
    signal_type: RewardSignal
    value: float
    metadata: Dict[str, Any]
    timestamp: float

class AutomaticIntermediateRewarding:
    """
    AIR System - Converts runtime signals into dense feedback

    Instead of sparse rewards at the end, provides immediate rewards
    for successful intermediate actions.
    """

    def __init__(self):
        # Base reward values for each signal type
        self.reward_values = {
            RewardSignal.TRIPLE_EXTRACTED: 0.2,
            RewardSignal.OWL_CONSISTENT: 1.0,
            RewardSignal.RUST_STORED: 0.1,
            RewardSignal.EMBEDDING_QUALITY: 0.5,  # Multiplied by similarity score
            RewardSignal.ONTOLOGY_MAPPED: 0.3,
            RewardSignal.CSV_PARSED: 0.1,
            RewardSignal.RAG_RELEVANT: 0.4,
            RewardSignal.QUERY_GENERATED: 0.3,
            RewardSignal.QUERY_VALID: 0.5,
            # User feedback (NUEVO - Agent Lightning)
            RewardSignal.USER_POSITIVE_FEEDBACK: 2.0,  # Alta recompensa por feedback positivo
            RewardSignal.USER_NEGATIVE_FEEDBACK: -1.0,  # Penalización por feedback negativo
        }

        # Penalty values
        self.token_cost_penalty = -0.01  # Per 100 tokens
        self.error_penalty = -0.5

        self.events: List[RewardEvent] = []

    def record_event(self, signal_type: RewardSignal, metadata: Dict[str, Any] = None):
        """Record a reward event"""
        import time

        if metadata is None:
            metadata = {}

        # Calculate reward value
        base_reward = self.reward_values.get(signal_type, 0.0)

        # Adjust based on metadata
        if signal_type == RewardSignal.EMBEDDING_QUALITY:
            similarity = metadata.get("similarity", 0.0)
            value = base_reward * similarity
        else:
            value = base_reward

        event = RewardEvent(
            signal_type=signal_type,
            value=value,
            metadata=metadata,
            timestamp=time.time()
        )

        self.events.append(event)
        return value

    def record_token_usage(self, token_count: int):
        """Record token usage (penalty)"""
        penalty = (token_count / 100) * self.token_cost_penalty
        import time

        event = RewardEvent(
            signal_type=RewardSignal.TRIPLE_EXTRACTED,  # Dummy type
            value=penalty,
            metadata={"tokens": token_count, "type": "cost_penalty"},
            timestamp=time.time()
        )
        self.events.append(event)
        return penalty

    def record_error(self, error_type: str):
        """Record an error (penalty)"""
        import time

        event = RewardEvent(
            signal_type=RewardSignal.TRIPLE_EXTRACTED,  # Dummy type
            value=self.error_penalty,
            metadata={"error": error_type},
            timestamp=time.time()
        )
        self.events.append(event)
        return self.error_penalty

    def get_total_reward(self) -> float:
        """Calculate total reward from all events"""
        return sum(event.value for event in self.events)

    def get_reward_breakdown(self) -> Dict[str, float]:
        """Get breakdown of rewards by signal type"""
        breakdown = {}
        for event in self.events:
            key = event.signal_type.value if isinstance(event.signal_type, RewardSignal) else "other"
            breakdown[key] = breakdown.get(key, 0.0) + event.value
        return breakdown

    def reset(self):
        """Clear all events"""
        self.events.clear()

    def get_summary(self) -> str:
        """Get human-readable summary"""
        total = self.get_total_reward()
        breakdown = self.get_reward_breakdown()

        summary = f"Total Reward: {total:.2f}\n"
        summary += "Breakdown:\n"
        for signal, value in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
            summary += f"  {signal}: {value:+.2f}\n"

        return summary

# Global AIR instance for tracking
_air_instance = None

def get_air() -> AutomaticIntermediateRewarding:
    """Get or create global AIR instance"""
    global _air_instance
    if _air_instance is None:
        _air_instance = AutomaticIntermediateRewarding()
    return _air_instance
