from typing import Optional
from .dataset_manager import DatasetManager, global_dataset_manager
from .configuration import DemoDataConfig

def generate_bank(config: Optional[DemoDataConfig] = None, seed: Optional[int] = None):
    """Entrypoint function to generate or refresh the synthetic financial data bank."""
    mgr = global_dataset_manager
    if config:
        mgr.config = config
    return mgr.generate_complete_dataset(seed=seed)
