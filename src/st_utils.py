import os
import json

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
    ensure_directory_exists(file_path.split("/")[1])
    write_file(file_path, dummy_data)


def write_base_templates(file_path: str, user: str):
    """TODO this should be abstracted into a generic initialization funtion."""
    dummy_data = {
        "user": user,
        "templates": [
            {
                "name": "None",
                "text": "{}"
            },
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
    ensure_directory_exists(file_path.split("/")[1])
    write_file(file_path, dummy_data)


def load_data(user: str, directory: str, filename_template: str = "{}.json"):
    '''Load data from file'''

    def is_json_file_empty(file_path):
        '''Checks if json file exists but is empty.'''
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
