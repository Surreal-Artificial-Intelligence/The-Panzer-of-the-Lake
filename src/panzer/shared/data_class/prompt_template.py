from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    id: Optional[int]
    name: str
    text: str
