from abc import ABC, abstractmethod
from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.embedding_response import EmbeddingResponse


class BaseModel(ABC):
    """Abstract class for all models"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def chat(self, messages) -> ModelResponse:
        pass

    @abstractmethod
    def image(self, prompt) -> ImageResponse:
        pass

    @abstractmethod
    def embedding(self, messages) -> EmbeddingResponse:
        pass
