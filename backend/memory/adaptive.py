import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class OptimizationPattern:
    context_key: str
    successful_strategies: List[str] = field(default_factory=list)
    failed_strategies: List[str] = field(default_factory=list)
    weight: float = 1.0


class AdaptiveMemory:
    """
    Implements Adaptive Learning (The 'Cognitive Evolution').
    Tracks patterns of success/failure to optimize future decisions.
    """

    def __init__(self, db_path: str = "data/adaptive_memory.json"):
        self.db_path = db_path
        self.patterns: Dict[str, OptimizationPattern] = {}
        self._load()

    def learn_outcome(self, context_key: str, strategy: str, success: bool):
        """Reinforce or discourage a strategy based on outcome."""
        if context_key not in self.patterns:
            self.patterns[context_key] = OptimizationPattern(context_key=context_key)

        pattern = self.patterns[context_key]

        if success:
            if strategy not in pattern.successful_strategies:
                pattern.successful_strategies.append(strategy)
            pattern.weight += 0.1
        else:
            if strategy not in pattern.failed_strategies:
                pattern.failed_strategies.append(strategy)
            pattern.weight = max(0.1, pattern.weight - 0.2)

        self._save()
        print(f"🧠 [Adaptive] Learned outcome for '{context_key}': {success}")

    def suggest_strategy(self, context_key: str) -> Optional[str]:
        """Suggests the best known strategy for a context."""
        if context_key in self.patterns:
            pattern = self.patterns[context_key]
            if pattern.successful_strategies:
                # Return most recent or best (simplified: most recent)
                return pattern.successful_strategies[-1]
        return None

    def _load(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, val in data.items():
                    self.patterns[key] = OptimizationPattern(**val)
        except (FileNotFoundError, json.JSONDecodeError):
            self.patterns = {}

    def _save(self):
        data = {key: vals.__dict__ for key, vals in self.patterns.items()}
        # Simple JSON dump (For Phase 12 MVP)
        # Ideally this goes to SQLite or Vector DB
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ [Adaptive] Save failed: {e}")
