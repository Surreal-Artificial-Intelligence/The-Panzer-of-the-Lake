from dataclasses import dataclass
import numpy as np
from typing import Optional, List


@dataclass
class VectorSearchResponse:
    """Represents a response from an vector storage system."""

    indices: List[int]

    distances: List[float]
