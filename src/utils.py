import os
import json
import random
from tinydb import TinyDB, Query
from config import DB_PATH
from data_class.prompt_template import PromptTemplate
from tinydb.table import Document

ENCODING = "utf-8"


def initialize_database(user: str):
    """Initialize the prompt template table."""
    if os.path.exists(f"{DB_PATH}/db.json"):
        return

    with TinyDB(DB_PATH) as db:
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


def load_templates(user: str):
    with TinyDB(DB_PATH) as db:
        results = db.table("prompt_template").search(Query().user == user)
        # iterate to get doc_id
        documents_with_ids = [PromptTemplate(id=doc.doc_id, name=doc["name"], text=doc["text"]) for doc in results]
        return documents_with_ids


def upsert_prompt_template(user: str, template: PromptTemplate):
    """Updates or creates a template in the database."""

    with TinyDB(DB_PATH) as db:
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


def read_file(file_name: str):
    """Read data from file"""
    with open(file_name, "r", encoding=ENCODING) as f:
        data = json.load(f)
    return data


def write_file(file_name: str, data) -> None:
    """Write data to file"""
    with open(file_name, "w", encoding=ENCODING) as f:
        f.write(json.dumps(data))


def ensure_directory_exists(directory_path):
    """Checks if a directory exists and if not creates it."""
    if not os.path.exists(directory_path):
        try:
            # Create the directory
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")


def write_dummy_data(file_path: str, user: str):
    """Write basic chats file"""
    dummy_data = {
        "user": f"{user}",
        "chats": [
            {
                "title": "",
                "content": [
                    {"role": "system", "content": "You are an AI assistant"},
                    {"role": "user", "content": "Hello, tell me about chats"},
                    {
                        "role": "assistant",
                        "content": "Hello! Chats are chats, come now?",
                    },
                ],
            }
        ],
    }
    ensure_directory_exists(file_path.split("/")[1])
    write_file(file_path, dummy_data)


def write_base_templates(file_path: str, user: str):
    """TODO this should be abstracted into a generic initialization funtion."""
    dummy_data = {
        "user": user,
        "templates": [
            {"name": "None", "text": "{}"},
            {"name": "Summarize", "text": "Summarize the following text: {}"},
            {"name": "Jokes", "text": "Give me jokes about the topic: {}"},
        ],
    }
    ensure_directory_exists(file_path.split("/")[1])
    write_file(file_path, dummy_data)


def load_data(user: str, directory: str, filename_template: str = "{}.json"):
    """Load data from file"""

    def is_json_file_empty(file_path):
        """Checks if json file exists but is empty."""
        try:
            return not bool(read_file(file_path))  # Check if the loaded data is empty
        except (json.JSONDecodeError, FileNotFoundError):
            return True

    file_name = os.path.join(directory, filename_template.format(user))
    if not os.path.exists(file_name) or is_json_file_empty(file_name):
        if directory == "./templates":
            write_base_templates(file_name, user)
        else:
            write_dummy_data(file_name, user)

    return read_file(file_name)


def save_prompt_template():
    """Save all prompt templates to file"""

    return list


def save_chats_to_file(user, data):
    "save chats to the user file"
    write_file(f"./chats/{user}.json", data)


def calculate_sleep_time(
    retries: int,
    initial_delay: float,
    backoff_factor: float,
    jitter: float,
    max_delay: float,
) -> float:
    """
    The function returns the calculated sleep time, which is then used by the continue_conversation function to
    pause execution before attempting another retry. The function calculates the sleep time using the following
    steps:

    1. Calculate the base sleep time by multiplying the `initial_delay` by the `backoff_factor` raised to the power
        of `retries`. This results in an exponential increase in sleep time with each retry.

    2. Add a random jitter value to the base sleep time. The jitter value is calculated as a random float between
        `-jitter * sleep_time and jitter * sleep_time`. This randomization helps avoid the synchronization of
        retries across multiple instances, which could lead to the "thundering herd" problem.

    3. Limit the sleep time to the `max_delay` value. This ensures that the delay between retries does not exceed
        a predefined maximum.

    Calculates the sleep time for a retry attempt using exponential backoff with jitter.

    Parameters
    ----------
    retries : int
        The number of retries that have been attempted so far.
    initial_delay : float
        The initial delay in seconds between retries.
    backoff_factor : float
        The factor by which the delay increases exponentially.
    jitter : float
        The random factor to apply to the sleep time calculation.
    max_delay : float
        The maximum delay in seconds between retries.

    Returns
    -------
    sleep_time : float
        The calculated sleep time in seconds.
    """
    sleep_time = initial_delay * (backoff_factor**retries)
    sleep_time += random.uniform(-jitter * sleep_time, jitter * sleep_time)
    return min(sleep_time, max_delay)


def log_retries(retries, sleep_time, e_rror):
    """Logs a message for retry attempts and sleep time.

    Parameters
    ----------
    retries : int
        The number of retries that have been attempted so far.
    sleep_time : float
    The calculated sleep time in seconds.

    """
    retry = f"Retry attempt {retries} failed. Waiting {sleep_time:.2f} seconds before trying again. Error: {e_rror}"
    return retry
