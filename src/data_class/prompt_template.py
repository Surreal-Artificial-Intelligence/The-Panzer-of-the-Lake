from dataclasses import dataclass


@dataclass
class PromptTemplate:
    id: int
    name: str
    text: str
