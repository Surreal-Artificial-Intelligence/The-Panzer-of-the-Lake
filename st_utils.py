import os
import re
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from tqdm import tqdm


ENCODING = "utf-8"


def fetch_embedding(string, progress_bar=None):
    """ Fetches the embedding for the given input string.
    Parameters
    ----------
    string : str
        The input string for which the embedding is to be fetched.
    progress_bar : tqdm, optional
        An instance of tqdm progress bar, used to update the progress. Default is None.

    Returns
    -------
    result : dict or None
        The embedding of the input string, or None if an error occurs.
    """
    url = os.environ["AZURE_OPENAI_ENDPOINT"]
    headers = {
        "Content-Type": "application/json",
        "api-key": os.environ["AZURE_OPENAI_SUBSCRIPTION_KEY"]
    }
    payload = json.dumps({"input": string})
    response = requests.post(url, headers=headers, data=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
    else:
        print(
            f"Error retrieving embedding for '{string}': {response.status_code} {response.text}")
        result = None

    if progress_bar:
        progress_bar.update(1)
    return result


def get_embeddings(strings):
    """ Fetches embeddings for a list of input strings using multithreading.
    Parameters
    ----------
    strings : list of str
        A list of input strings for which embeddings are to be fetched.

    Returns
    -------
    embeddings : list of dict
        A list of embeddings for the input strings.
    """
    with ThreadPoolExecutor(max_workers=8) as executor:
        with tqdm(total=len(strings)) as progress_bar:
            # Submit all tasks and store their futures with corresponding index
            futures = {executor.submit(
                fetch_embedding, string, progress_bar): idx for idx, string in enumerate(strings)}

            # Initialize an empty list for embeddings
            embeddings = [None] * len(strings)

            # Collect results as they complete, and put them in their original order
            for future in as_completed(futures):
                idx = futures[future]
                embeddings[idx] = future.result()

    return embeddings


def format_knowledge(vector_results):
    """ Formats knowledge elements based on vector results.

    Parameters
    ----------
    vector_results : dict
        The vector results containing documents and metadatas.

    Returns
    -------
    knowledge_elements : list of str
        A list of formatted knowledge elements.
    """
    knowledge_elements = []

    for page, metadata in zip(vector_results['documents'][0], vector_results['metadatas'][0]):
        knowledge_element = f'<knowledge text="{page}" source="{{ title: \'{metadata["title"]}\', source=\'{metadata["source"]}\' }}"></knowledge> \n'
        knowledge_elements.append(knowledge_element)
    return knowledge_elements


def read_file(file_name: str):
    """Read data from file"""
    with open(file_name, "r", encoding=ENCODING) as f:
        data = json.load(f)
    return data


def write_file(file_name: str, data) -> None:
    """Write data to file"""
    with open(file_name, "w", encoding=ENCODING) as f:
        f.write(json.dumps(data))


def is_json_file_empty(file_path):
    '''Checks if json file exists but is empty.'''
    try:
        return not bool(read_file(file_path))  # Check if the loaded data is empty
    except (json.JSONDecodeError, FileNotFoundError):
        return True


def create_directory(directory_path):
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
    '''Write basic chats file'''
    dummy_data = {
        "user": f"{user}",
        "chats": [
            {
                "title": "",
                "content": [
                    {
                        "role": "system",
                        "content": "You are an AI assistant"
                    },
                    {
                        "role": "user",
                        "content": "Hello, tell me about chats"
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! Chats are chats, come now?"
                    }
                ]
            }
        ]
    }
    write_file(file_path, dummy_data)


def write_base_templates(file_path: str, user: str):
    """TODO this should be abstracted into a generic initialization funtion."""
    dummy_data = {
        "user": user,
        "templates": [
            {
                "name": "Summarize",
                "text": "Summarize the following text: {}"
            },
            {
                "name": "Jokes",
                "text": "Give me jokes about the topic: {}"
            }
        ]
    }
    write_file(file_path, dummy_data)


def load_chats(user: str):
    '''Load chats from json file'''
    file_name = f"./chats/{user}.json"

    if not os.path.exists(file_name) or is_json_file_empty(file_name):
        write_dummy_data(file_name, user)

    return read_file(file_name)


def save_chats_to_file(user, data):
    "save chats to the user file"
    write_file(f"./chats/{user}.json", data)


def load_prompt_templates(user: str):
    """Load all prompt templates from file"""
    file_name = f"./templates/{user}.json"

    if not os.path.exists(file_name) or is_json_file_empty(file_name):
        write_dummy_data(file_name, user)

    return read_file(file_name)


def load_data(user: str, directory: str, filename_template: str = "{}.json"):
    '''Load data from file'''
    file_name = os.path.join(directory, filename_template.format(user))

    if not os.path.exists(file_name) or is_json_file_empty(file_name):
        write_dummy_data(file_name, user)

    return read_file(file_name)


def save_prompt_template():
    """Save all prompt templates to file"""

    return list
