from dataclasses import dataclass
from typing import List, Optional



@dataclass
class AIModel:
    id: str
    created: int
    type: str
    display_name: str
    organization: str
    license: Optional[str]
    context_length: Optional[int]
    price_input: float
    price_output: float

