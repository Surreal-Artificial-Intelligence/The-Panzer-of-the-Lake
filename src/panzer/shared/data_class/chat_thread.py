from dataclasses import dataclass, asdict
from typing import List
from .chat_message import ChatMessage


@dataclass
class ChatThread:
    title: str
    created_date: str
    messages: List[ChatMessage]
    usage: int

    def messages_to_dict(self):
        return [asdict(message) for message in self.messages]
