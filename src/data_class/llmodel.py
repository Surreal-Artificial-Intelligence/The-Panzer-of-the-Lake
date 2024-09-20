from dataclasses import dataclass
from enums.organization import Organization


@dataclass
class LLModel():

    organization: Organization
    model_name: str
    context_length: int
