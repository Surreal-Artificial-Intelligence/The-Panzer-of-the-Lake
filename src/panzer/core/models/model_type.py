from enum import Enum


class ModelType(Enum):
    """Model type."""
    TEXT = "text"
    IMAGE = "image"
    MOE = "moe"
    RAG = "rag"
