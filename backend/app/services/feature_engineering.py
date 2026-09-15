"""6-Stage Feature Engineering Pipeline."""
from typing import Tuple, Optional

def normalize_degree(degree_str: Optional[str]) -> Tuple[str, int]:
    if not degree_str: return "None", 0
    return str(degree_str), 1
