from dataclasses import dataclass
from typing import List, Optional


@dataclass
class EmbeddingResponse:
    """Represents a response from an embedding model."""

    embeddings: List[List[float]]

    metadata: Optional[dict] = None
