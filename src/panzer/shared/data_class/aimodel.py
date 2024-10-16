from dataclasses import dataclass
from core.models.provider import Provider


@dataclass
class AIModel:
    organization: Provider
    model_name: str
    context_length: int
