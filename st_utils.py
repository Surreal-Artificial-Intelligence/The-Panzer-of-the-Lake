import os
import time
import random
import requests
import re
import json

import streamlit as st

from tqdm import tqdm
# import openai

from concurrent.futures import ThreadPoolExecutor, as_completed

# openai.api_type = "azure"
# openai.api_base = st.secrets["AZURE_BASE"]
# openai.api_version = "2023-03-15-preview"
# openai.api_key = st.secrets["AZURE_OPENAI_SUBSCRIPTION_KEY"]


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
    response = requests.post(url, headers=headers, data=payload)

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


def find_query(text):
    """ Extracts queries enclosed between <q> and </q> tags from a given text.

    Parameters
    ----------
    text : str
        The input text containing query tags.

    Returns
    -------
    matches : list of str
        A list of queries extracted from the input text.
    """
    pattern = r'<q>(.*?)<\/q>'
    matches = re.findall(pattern, text)
    return matches


def query_chroma(query_embeddings, collection: str):
    """ Queries the Chroman Database API with the given embeddings and collection name.
    Parameters
    ----------
    query_embeddings : list of dict
        A list of query embeddings.
    collection : str
        The name of the collection to be queried.

    Returns
    -------
    response : dict
        The JSON response from the Chroma API.
    """
    url = f"http://localhost:8000/api/v1/collections/{collection}/query"

    payload = {
        "query_embeddings": [query_embeddings],
        "n_results": 5,  # The number of nearest neighbors to return
        # Fields to include in the response
        "include": ["documents", "embeddings", "metadatas", "distances"],
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Query executed successfully.")
        # print(response.json())
    else:
        print("Error occurred:", response.status_code, response.text)
    return response.json()


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


def load_chats(user: str):
    file_name = f"./chats/{user}.json"
    # Check if the file exists
    if not os.path.exists(file_name):
        # If not, create it with the basic structure
        data = {
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
                            "content": "hello, tell me about chats"
                        },
                        {
                            "role": "assistant",
                            "content": "Hello! Chats are chats, come now?"
                        }
                    ]
                }
            ]
        }

        with open(file_name, "w") as f:
            f.write(json.dumps(data))
    else:
        # If the file exists, read the dictionary from the text file
        with open(file_name, "r") as f:
            data = json.loads(f.read())
            # print(data)

    return data


def save_chats_to_file(user, data):
    with open(f"./chats/{user}.json", "w") as f:
        f.write(json.dumps(data))
