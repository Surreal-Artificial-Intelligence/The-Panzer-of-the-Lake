from data_class.prompt_template import PromptTemplate
import os
from tinydb import Query, TinyDB
from tinydb.table import Document


class TinyDBAccess:
    """TinyDB access class"""

    def __init__(self, db_dir: str):
        self.db_path = f"{db_dir}/db.json"
        self.db_dir = db_dir

    def initialize_database(self, user: str):
        """Initialize the prompt template table."""
        if os.path.exists(self.db_path):
            return

        # create the db path if it does not exist
        os.makedirs(self.db_dir, exist_ok=True)

        with TinyDB(self.db_path) as db:
            templates = [
                {"user": user, "name": "None", "text": "{}"},
                {
                    "user": user,
                    "name": "Summarize",
                    "text": "Summarize the following text: {}",
                },
                {
                    "user": user,
                    "name": "Jokes",
                    "text": "Give me jokes about the topic: {}",
                },
            ]

            table = db.table("prompt_template")

            existing_templates = table.search((Query().name == "None") and (Query().user == user))

            if existing_templates:
                return

            table.insert_multiple(templates)

        print("Prompt templates initialized.")

    def load_templates(self, user: str):
        """Loads the templates from the database."""
        with TinyDB(self.db_path) as db:
            results = db.table("prompt_template").search(Query().user == user)
            # iterate to get doc_id
            documents_with_ids = [PromptTemplate(id=doc.doc_id, name=doc["name"], text=doc["text"]) for doc in results]
            return documents_with_ids

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
