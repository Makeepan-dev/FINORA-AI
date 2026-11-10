import random
from typing import Optional

class SeedManager:
    """Manages deterministic random seeds across data generation runs."""
    def __init__(self, default_seed: int = 42):
        self._current_seed = default_seed

    @property
    def current_seed(self) -> int:
        return self._current_seed

    def set_seed(self, seed: int):
        self._current_seed = seed
        random.seed(seed)

    def get_rng(self, sub_component: Optional[str] = None) -> random.Random:
        if sub_component:
            # Deterministically derive component seed
            h = hash(sub_component) & 0xFFFFFFFF
            return random.Random(self._current_seed ^ h)
        return random.Random(self._current_seed)

global_seed_manager = SeedManager(42)
