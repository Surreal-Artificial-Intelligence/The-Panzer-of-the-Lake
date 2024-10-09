from dataclasses import dataclass
import numpy as np
from typing import Optional


@dataclass
class EmbeddingResponse:
    """Represents a response from an embedding model."""

    embeddings: np.ndarray

    metadata: Optional[dict] = None
