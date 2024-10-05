from abc import ABC, abstractmethod
from data_class.model_response import ModelResponse


class BaseModel(ABC):
    """Abstract class for all models"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> str:
        pass

    @abstractmethod
    def chat(self, messages) -> ModelResponse:
        pass
