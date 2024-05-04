import json
import requests
import numpy as np

import streamlit as st
from streamlit_extras.colored_header import colored_header

from ollama_model import OllamaModel
from open_ai_model import OpenAIModel
from openai_azure_model import OpenAIAzureModel
# from xtts_v2_model import XTTSV2Model

from config import SUPPORTED_MODELS


from st_utils import (
    save_chats_to_file,
    load_chats,
)


st.set_page_config(
    page_title="POTL",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"}
)

colored_header(label="Panzer of the Lake",
               description="Welcome to the lake ask your question so the Panzer may answer it.",
               color_name="blue-green-70"
               )


# Utility Functions
chat_container = st.container()
chat_container.empty()
text_area_container = st.container()
text_area_container.empty()
side_chats_container = st.container()
side_chats_container.empty()


def initialize_session_variables() -> None:
    """Initializes session variables"""

    if 'chat_history' not in st.session_state:
        st.session_state["chat_history"] = {"title": "", "content": [
            {"role": "system", "content": "You are an all-knowing, highly compliant AI assistant."}]}

    if 'output' not in st.session_state:
        st.session_state["output"] = ""

    if 'containers' not in st.session_state:
        st.session_state["containers"] = {}

    if 'total_tokens_used' not in st.session_state:
        st.session_state["total_tokens_used"] = 0

    if 'chats' not in st.session_state:
        st.session_state["chats"] = load_chats("Emile")

    if 'model' not in st.session_state:
        st.session_state["model"] = None

    if 'hyperparameters' not in st.session_state:
        temperature = 0.5
        max_token = 5000
        top_prob = 0.95
        frequency_penalty = 0.0
        presence_penalty = 0.0
        st.session_state["hyperparameters"] = {
            "temperature": temperature,
            "max_tokens": max_token,
            "top_p": top_prob,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty}


initialize_session_variables()


@st.cache_resource
def get_openai_connection():
    """Instantiate and return the OpenAI model client"""
    client = OpenAIModel(api_key=st.secrets['OPENAI_API_KEY'], model_name="gpt-3.5-turbo-0613")
    return client


@st.cache_resource
def get_openai_azure_connection():
    """Instantiate and return the AzureOpenAI model client"""
    client = OpenAIAzureModel(api_key=st.secrets['AZURE_OPENAI_API_KEY'],
                              api_version=st.secrets['AZURE_API_VERSION'],
                              azure_endpoint=st.secrets['AZURE_OPENAI_BASE'],
                              model_name=st.secrets['AZURE_OPENAI_DEPLOYMENT'])
    return client


@st.cache_resource
def get_ollama_connection(url: str = "http://localhost:11434/api/chat",
                          model_label: str = "mistral"):
    """Instantiate and return the Ollama model client"""
    client = OllamaModel(url, model_label)
    return client


# @st.cache_resource
# def get_custom_tts_connection():
#     url = "http://localhost:11434/api/generate"
#     client = local_model(url)
#     return client


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
            if item["role"] == 'assistant':
                with st.chat_message(item["role"], avatar='./tankfinal2.png'):
                    st.markdown(item['content'])
            else:
                with st.chat_message(item["role"]):
                    st.markdown(item['content'])


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
                    color_name="blue-green-70"
                )
                col_load.button("Load", on_click=load_conversation, args=(i,), key=i, use_container_width=True)
                col_delete.button("🗑", on_click=delete_conversation, args=(i,), key=i+10000, use_container_width=True)


def update_chat_history(role: str, text_response: str):
    """Appends new content to the chat history session variable"""
    st.session_state["chat_history"]["content"].append({'role': role, 'content': text_response})
    return


voice_enabled = False
with st.sidebar:

    model_name = st.selectbox('Model:', SUPPORTED_MODELS)
    st.divider()
    voice_enabled = st.checkbox("Voice")
    hyperparameters_enabled = st.checkbox("Hyperparameters")
    if hyperparameters_enabled:
        st.markdown("# Hyperparameters")
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        max_t = st.number_input("Max Tokens", 0, 15000, 20000, 10)
        top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.01)
        f_pen = st.slider("Frequency Penalty", 0.0, 2.0, 0.0, 0.1)
        p_pen = st.slider("Presence Penalty", 0.0, 2.0, 0.0, 0.1)
        st.session_state["hyperparameters"] = {
            "temperature": temp,
            "max_tokens": max_t,
            "top_p": top_p,
            "frequency_penalty": f_pen,
            "presence_penalty": p_pen
        }
    side_chats_container = st.container()
    side_chats_container.empty()
    with side_chats_container:
        populate_chats(st.session_state["chats"])


def query_text_to_speech_api(text: str, lang: str = 'en'):
    """Gets speech audio from tts endpoint"""
    api_url = "http://localhost:8000/text-to-speech"
    try:
        # Sending a POST request
        data = {
            "text": text,
            "lang": lang
        }

        tts_response = requests.post(api_url, headers="headerss", json=data)

        if tts_response.status_code == 200:

            # Decode the binary data to a string
            json_string = tts_response.content.decode('utf-8')
            # Convert the JSON string to a Python list
            audio_list = json.loads(json_string)
            audio_array = np.array(audio_list)
            return audio_array
        else:
            print(f"Error: {tts_response.status_code} - {tts_response.text}")
    except Exception as e:
        # Print an error message in case of an exception
        print(f"Exception: {str(e)}")


def generate_response(messages):
    """Calls a specific model client to get a response"""

    if model_name == "OpenAI":
        client = get_openai_connection()
    elif model_name == "Azure":
        client = get_openai_azure_connection()
    else:
        client = get_ollama_connection(model_label=model_name)

    return client.chat(messages)


def process_query(query_string: str) -> None:
    """Handles user input"""

    with st.status("I'm thinking...", expanded=False) as status:
        with text_area_container:

            update_chat_history("user", query_string)
            render_chats()

            chat_response = generate_response(st.session_state["chat_history"]["content"])

            if model_name == "OpenAI" or model_name == 'Azure':
                text_response = chat_response.choices[0].message.content
                st.session_state["total_tokens_used"] = chat_response.usage.total_tokens
            else:
                text_response = chat_response["message"]["content"]

            update_chat_history("assistant", text_response)
            quicksave_chat()
            save_chats_to_file(st.session_state["chats"]["user"], st.session_state["chats"])

            if voice_enabled:
                status.update(label="Weaving resonance...", state="running", expanded=False)
                return query_text_to_speech_api(text=text_response)
            else:
                return text_response


if query := st.chat_input("O Panzer of the Lake, what is your wisdom?"):
    # st.chat_message('user').write(query)

    response = process_query(query)
    if voice_enabled:
        with st.chat_message('ai', avatar='./tankfinal2.png'):
            st.write("Hear ye, hear ye.")
            st.audio(response, format='audio/wav', sample_rate=24000)
    else:
        st.chat_message('ai', avatar='./tankfinal2.png').write(response)
        st.write("Total tokens:", st.session_state["total_tokens_used"])
