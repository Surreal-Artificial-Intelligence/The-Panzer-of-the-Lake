from abc import ABC, abstractmethod
from data_class.model_response import ModelResponse
from data_class.image_response import ImageResponse
from data_class.embedding_response import EmbeddingResponse


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
