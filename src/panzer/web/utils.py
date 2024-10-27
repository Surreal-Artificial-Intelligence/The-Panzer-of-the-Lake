import os
import json
import random
import base64
from shared.data_class.aimodel import AIModel
from core.models.provider import Provider
from typing import List, Optional, Dict
from web.config import CHATS_PATH

ENCODING = "utf-8"


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
    write_file(f"{CHATS_PATH}/{user}.json", data)


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


def encode_image(image):
    """Open the image file and encode it as a base64 string"""
    return base64.b64encode(image).decode("utf-8")


def load_model_configs() -> list[AIModel]:
    with open("models.json", "r") as file:
        model_data = json.load(file)

    ll_models = []
    # for organization, models in model_data.items():
    #     for model in models:
    #         ll_models.append(
    #         )
    # TODO: Figure out how to load configs for other models.
    return ll_models
