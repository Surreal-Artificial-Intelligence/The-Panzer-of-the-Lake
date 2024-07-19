from abc import ABC, abstractmethod
from model_utils import calculate_sleep_time, log_retries

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
    
    