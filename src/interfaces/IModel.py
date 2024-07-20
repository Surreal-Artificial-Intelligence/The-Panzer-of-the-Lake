from abc import ABC, abstractmethod


class IModel(ABC):
    """Abstract class for all models"""

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> str:
        pass

    @abstractmethod
    def chat(self) -> str:
        pass
