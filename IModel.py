from abc import ABC, abstractmethod


class IModel(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def test_connection(self) -> str:
        pass

    @abstractmethod
    def chat(self) -> str:
        pass
