import os
from dataclasses import asdict

from pathlib import Path
from shared.data_class.prompt_template import PromptTemplate
from shared.data_class.chat_thread import ChatThread
from shared.data_class.chat_thread import ChatMessage
from shared.data_class.chat_user import ChatUser

from tinydb import Query, TinyDB
from tinydb.table import Document


class TinyDBAccess:
    """TinyDB access class"""

    def __init__(self, db_dir: str):
        self.db_path = f"{db_dir}/db.json"
        self.db_dir = db_dir

    def initialize_database(self, user: str):
        """Initialize all tables."""

        file_path = Path(self.db_path)
        if file_path.is_file():
            return

        print("Database does not exist, creating...")
        os.makedirs(self.db_dir, exist_ok=True)

        with TinyDB(self.db_path) as db:
            prompts_table = db.table("prompt_template")
            chats_table = db.table("chat_threads")

            template_dummy = [
                {"user": user, "name": "None", "text": "{}"},
                {
                    "user": user,
                    "name": "Summarize",
                    "text": "Summarize the following text: {}",
                },
            ]

            chat_dummy = [
                {
                    "user": "Emile",
                    "chats": [
                        {
                            "title": "Basic Chat 1",
                            "created_date": "2019-05-31",
                            "usage": "5",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are an all-knowing, highly compliant AI assistant."
                                },
                                {"role": "assistant", "content": "Test chat"},
                            ],
                        }
                    ],
                },
                {
                    "user": "Bob",
                    "chats": [
                        {
                            "title": "Basic Chat 2",
                            "created_date": "2020-05-31",
                            "usage": "5",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are an all-knowing, highly compliant AI assistant."
                                },
                                {"role": "assistant", "content": "Test chat 2"},
                            ],
                        }
                    ],
                },
            ]

            if len(prompts_table.search((Query().name == "None") and (Query().user == user))) == 0:
                prompts_table.insert_multiple(template_dummy)

            if len(chats_table.search((Query().name == "None") and (Query().user == user))) == 0:
                chats_table.insert_multiple(chat_dummy)

        print("Database successfully initialized.")

    def load_templates(self, user: str):
        """Loads the templates from the database."""
        with TinyDB(self.db_path) as db:
            results = db.table("prompt_template").search(Query().user == user)
            documents_with_ids = [PromptTemplate(id=doc.doc_id, name=doc["name"], text=doc["text"]) for doc in results]
            return documents_with_ids

    def load_chat_user(self, user: str):
        """Loads the chats from the database."""
        with TinyDB(self.db_path) as db:
            results = db.table("chat_threads").search(Query().user == user)
            documents_with_ids = [
                ChatUser(
                    id=doc.doc_id,
                    user=doc["user"],
                    chats=[
                        ChatThread(
                            title=chatt["title"],
                            created_date=chatt["created_date"],
                            usage=chatt["usage"],
                            messages=[
                                ChatMessage(role=message["role"], content=message["content"])
                                for message in chatt["messages"]
                            ],
                        )
                        for chatt in doc["chats"]
                    ],
                )
                for doc in results
            ]

            if len(documents_with_ids) > 1:
                raise ValueError("More than one chat user found", len(documents_with_ids) )
            else:
                return documents_with_ids[0]

    def upsert_chat_user(self, chat_user: ChatUser):
        """Updates or creates a chat_user in the database."""

        with TinyDB(self.db_path) as db:
            if chat_user.id is None:
                db.table("chat_threads").insert(asdict(chat_user))
            else:
                db.table("chat_threads").upsert(Document({"chats": self.convert_dataclass_to_dict(chat_user.chats)}, doc_id=chat_user.id))

    def upsert_prompt_template(self, user: str, template: PromptTemplate):
        """Updates or creates a template in the database."""

        with TinyDB(self.db_path) as db:
            if template.id is None:
                db.table("prompt_template").insert(
                    {
                        "user": user,
                        "name": template.name,
                        "text": template.text,
                    }
                )
            else:
                db.table("prompt_template").upsert(
                    Document({"name": template.name, "text": template.text}, doc_id=template.id)
                )

    def convert_dataclass_to_dict(self, obj):
        if isinstance(obj, list):
            return [self.convert_dataclass_to_dict(item) for item in obj]
        elif isinstance(obj, ChatUser) or isinstance(obj, ChatThread) or isinstance(obj, ChatMessage):
            return asdict(obj)
        else:
            return obj