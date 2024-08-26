import io
from io import StringIO
import json
from typing import List
import requests
import numpy as np

import streamlit as st
from streamlit_extras.colored_header import colored_header

from ollama_model import OllamaModel
from open_ai_model import OpenAIModel
from azure_openai_model import AzureOpenAIModel
from azure_cohere_model import CohereAzureModel
from tinydb_access import TinyDBAccess

from config import (
    SUPPORTED_MODELS,
    ASSETS_PATH,
    CHATS_PATH,
    LOGO_CONFIG,
    DB_PATH,
)

from PIL import Image

from utils import save_chats_to_file, load_data, log_retries, encode_image

st.set_page_config(
    page_title="POTL",
    page_icon=f"{ASSETS_PATH}/surreal-logo.jpg",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"},
)

colored_header(
    label="Panzer of the Lake",
    description="Welcome to the lake ask your question so the Panzer may answer it.",
    color_name="blue-green-70",
)


st.logo(**LOGO_CONFIG)


# Utility Functions
chat_container = st.container()
chat_container.empty()
text_area_container = st.container()
text_area_container.empty()
side_chats_container = st.container()
side_chats_container.empty()


@st.cache_resource
def get_openai_connection(model_label: str = "gpt-4o"):
    """Instantiate and return the OpenAI model client"""
    client = OpenAIModel(api_key=st.secrets["OPENAI_API_KEY"], model_name=model_label)
    return client


@st.cache_resource
def get_openai_azure_connection(model_label: str = "gpt-4o"):
    """Instantiate and return the AzureOpenAI model client"""
    client = AzureOpenAIModel(
        api_key=st.secrets["AZURE_OPENAI_API_KEY"],
        api_version=st.secrets["AZURE_API_VERSION"],
        azure_endpoint=st.secrets["AZURE_OPENAI_BASE"],
        model_name=st.secrets["AZURE_OPENAI_DEPLOYMENT"],
    )
    return client


@st.cache_resource
def get_cohere_azure_connection(model_label: str = "command-r-plus"):
    """Instantiate and return the CohereAzure model client"""
    client = CohereAzureModel(
        api_key=st.secrets["AZURE_COHERE_API_KEY"],
        api_version=st.secrets["AZURE_API_VERSION"],
        azure_endpoint=st.secrets["AZURE_COHERE_BASE"],
        model_name=st.secrets["AZURE_COHERE_DEPLOYMENT"],
    )
    return client


@st.cache_resource
def get_ollama_connection(url: str = "http://localhost:11434/api/chat", model_label: str = "mistral"):
    """Instantiate and return the Ollama model client"""
    client = OllamaModel(url, model_label)
    return client


@st.cache_resource
def get_tinydb_client(db_path: str) -> TinyDBAccess:
    """Instantiate and return the TinyDB access client"""
    client = TinyDBAccess(db_path)
    return client


# @st.cache_resource
# def get_custom_tts_connection():
#     url = "http://localhost:11434/api/generate"
#     client = local_model(url)
#     return client


def initialize_session_variables() -> None:
    """Initializes session variables and loads user data."""
    tinydb_client = get_tinydb_client(DB_PATH)

    if "DB_PATH" not in st.session_state:
        st.session_state["DB_PATH"] = DB_PATH

    if "user" not in st.session_state:
        st.session_state["user"] = "Emile"

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = {
            "title": "",
            "content": [
                {
                    "role": "system",
                    "content": "You are an all-knowing, highly compliant AI assistant.",
                }
            ],
        }

    if "chats" not in st.session_state:
        st.session_state["chats"] = load_data("Emile", CHATS_PATH)

    if "templates" not in st.session_state:
        tinydb_client.initialize_database(st.session_state["user"])
        st.session_state["templates"] = tinydb_client.load_templates(st.session_state["user"])

    if "model" not in st.session_state:
        st.session_state["model"] = None

    if "total_tokens_used" not in st.session_state:
        st.session_state["total_tokens_used"] = 0

    if "image" not in st.session_state:
        st.session_state["image"] = {"file_name": "", "content": ""}

    if "hyperparameters" not in st.session_state:
        st.session_state["hyperparameters"] = {
            "temperature": 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }


initialize_session_variables()


def quicksave_chat():
    """
    Saves the current chat that is in chat history into the all user chats variable.
    Basically a quicksave function.
    """
    if st.session_state["chat_history"] not in st.session_state["chats"]["chats"]:
        st.session_state["chats"]["chats"].append(st.session_state["chat_history"])
    else:
        # overwrite existing one
        for i, item in enumerate(st.session_state["chats"]["chats"]):
            if item == st.session_state["chat_history"]:
                st.session_state["chats"]["chats"][i] = st.session_state["chat_history"]
                break


def reset_stats():
    """Sets chat statistics to zero"""
    st.session_state["total_tokens_used"] = 0


def render_chats():
    """Renders chats in bubbles in the UI"""
    chat_container.empty()
    with chat_container:
        for item in st.session_state["chat_history"]["content"][1:]:
            if item["role"] == "assistant":
                with st.chat_message(item["role"], avatar=f"{ASSETS_PATH}/tank.jpeg"):
                    st.markdown(item["content"])
            else:
                with st.chat_message(item["role"]):
                    st.markdown(item["content"])


def populate_chats(user_chats):
    """Loads conversation from file memory"""

    def load_conversation(i: int):
        st.session_state["chat_history"] = user_chats["chats"][i]
        render_chats()

    def delete_conversation(i: int):
        del user_chats["chats"][i]
        save_chats_to_file(st.session_state["chats"]["user"], user_chats)

    for i, item in enumerate(user_chats["chats"]):
        chat_tile_container = st.container()
        col_load, col_delete = st.columns(2)
        with chat_tile_container:
            if item:
                colored_header(
                    label="",
                    description=item["content"][1]["content"][:70],
                    color_name="blue-green-70",
                )
                col_load.button(
                    "Load",
                    on_click=load_conversation,
                    args=(i,),
                    key=i,
                    use_container_width=True,
                )
                col_delete.button(
                    "🗑",
                    on_click=delete_conversation,
                    args=(i,),
                    key=i + 10000,
                    use_container_width=True,
                )


def update_chat_history(chat_content: dict):
    """Appends new content to the chat history session variable"""
    st.session_state["chat_history"]["content"].append(chat_content)
    return


@st.dialog("Attach your media.")
def file_uploader():
    file = st.file_uploader("Upload your media.", type=["png", "jpg"], key="media")
    if file:
        bytes_data = file.getvalue()
        st.image(bytes_data, caption=file.name, use_column_width=True)

    confirm = st.button("Confirm")
    if confirm and file:
        encoded_image = encode_image(bytes_data)
        st.session_state["image"] = {"file_name": file.name, "content": encoded_image}
        st.rerun()


voice_enabled = False
with st.sidebar:
    corporation = st.selectbox("Corporation:", SUPPORTED_MODELS.keys())
    model_name = st.selectbox("Model:", SUPPORTED_MODELS[corporation])  # type: ignore
    template_name = st.selectbox("Prompt Template:", [item.name for item in st.session_state["templates"]])
    st.divider()
    image = st.button("Attach image", on_click=file_uploader)
    st.write(st.session_state["image"]["file_name"])
    st.divider()
    voice_enabled = st.checkbox("Voice")

    hyperparameters_enabled = st.checkbox("Hyperparameters")
    if hyperparameters_enabled:
        st.markdown("# Hyperparameters")
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        st.session_state["hyperparameters"] = {
            "temperature": temp,
        }
    st.divider()
    side_chats_container = st.container()
    side_chats_container.empty()
    with side_chats_container:
        populate_chats(st.session_state["chats"])


def query_text_to_speech_api(text: str, lang: str = "en"):
    """Gets speech audio from tts endpoint"""
    api_url = "http://localhost:8000/text-to-speech"
    try:
        # Sending a POST request
        data = {"text": text, "lang": lang}

        tts_response = requests.post(api_url, headers="headers", json=data)

        if tts_response.status_code == 200:
            # Decode the binary data to a string
            json_string = tts_response.content.decode("utf-8")
            # Convert the JSON string to a Python list
            audio_list = json.loads(json_string)
            audio_array = np.array(audio_list)
            return audio_array
        else:
            print(f"Error: {tts_response.status_code} - {tts_response.text}")
    except Exception as e:
        # Print an error message in case of an exception
        print(f"Exception: {str(e)}")


corporation_clients = {
    "OpenAI": get_openai_connection,
    "Azure": get_openai_azure_connection,
    "Ollama": get_ollama_connection,
}


def generate_response(messages):
    """Calls a specific model client to get a response"""

    if corporation in corporation_clients:
        client = corporation_clients.get(corporation, "Ollama")(model_label=model_name)  # type: ignore
        return client.chat(messages, on_retry=log_retries)
    else:
        raise ValueError(f"Invalid model name: {model_name}")


def process_query(query_string: str) -> None:
    """Handles user input"""

    with st.status("I'm thinking...", expanded=False) as status:
        with text_area_container:
            # TODO search by id or by direct db query
            selected_template = [t.text for t in st.session_state["templates"] if t.name == template_name][0]
            templated_message = selected_template.format(query_string)
            # if image attached
            if not st.session_state["image"]["content"] == "" and (corporation == "OpenAI" or corporation == "Azure"):
                templated_message = [
                    {"type": "text", "text": templated_message},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{st.session_state['image']['content']}"},
                    },
                ]
                st.session_state["image"] = ""
                update_chat_history({"role": "user", "content": templated_message})
            else:
                update_chat_history({"role": "user", "content": templated_message, "images": [st.session_state["image"]["content"]]})

            render_chats()

            chat_response = generate_response(st.session_state["chat_history"]["content"])

            if corporation == "OpenAI" or corporation == "Azure":
                text_response = chat_response.choices[0].message.content
                st.session_state["total_tokens_used"] = chat_response.usage.total_tokens
            else:
                text_response = chat_response["message"]["content"]

            update_chat_history({"role": "assistant", "content": text_response})

            quicksave_chat()
            save_chats_to_file(st.session_state["chats"]["user"], st.session_state["chats"])

            if voice_enabled:
                status.update(label="Weaving resonance...", state="running", expanded=False)
                # return query_text_to_speech_api(text=text_response)
            else:
                return text_response


if query := st.chat_input("O Panzer of the Lake, what is your wisdom?"):
    response = process_query(query)
    if voice_enabled:
        with st.chat_message("ai", avatar=f"{ASSETS_PATH}/tank.jpeg"):
            st.write("Hear ye, hear ye.")
            st.audio(response, format="audio/wav", sample_rate=24000)
    else:
        st.chat_message("ai", avatar=f"{ASSETS_PATH}/tank.jpeg").write(response)
        st.write("Total tokens:", st.session_state["total_tokens_used"])
