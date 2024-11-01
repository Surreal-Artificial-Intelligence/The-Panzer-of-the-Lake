from dataclasses import dataclass
from typing import List, Optional
from .chat_thread import ChatThread


@dataclass
class ChatUser:
    id: Optional[int]
    user: str
    chats: List[ChatThread]

