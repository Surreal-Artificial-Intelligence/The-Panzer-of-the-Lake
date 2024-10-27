from abc import ABC, abstractmethod
from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.responses.embedding_response import EmbeddingResponse


class BaseModelClient(ABC):
    """Abstract class for all models"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def models(self):
        pass

    @abstractmethod
    def chat(self, model_name: str, messages) -> ModelResponse:
        pass

    @abstractmethod
    def image(self, model_name: str, prompt) -> ImageResponse:
        pass

    @abstractmethod
    def embedding(self, model_name: str, messages) -> EmbeddingResponse:
        pass
