import json
import requests
import numpy as np
import streamlit as st
from streamlit_extras.colored_header import colored_header
from utils import (
    save_chats_to_file,
    load_chats,
    continue_conversation,
    log_retries
)

st.set_page_config(
    page_title="Sensei",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"}
)

colored_header(label="Panzer of the Lake", description="Welcome to the lake,"
               " ask your question so the Panzer may answer it.",
               color_name="blue-green-70")


# Utility Functions
chat_container = st.container()
chat_container.empty()
text_area_container = st.container()
text_area_container.empty()
side_chats_container = st.container()
side_chats_container.empty()


def set_session_variables() -> None:

    if 'chat_history' not in st.session_state:
        st.session_state["chat_history"] = {"title": "", "content": [
            {"role": "system", "content": "You are an AI assistant"}]}

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
        temp = 0.5
        max_t = 5000
        top_p = 0.95
        f_pen = 0.0
        p_pen = 0.0
        st.session_state["hyperparameters"] = {
            "temperature": temp,
            "max_tokens": max_t,
            "top_p": top_p,
            "frequency_penalty": f_pen,
            "presence_penalty": p_pen}


set_session_variables()


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


def populate_chats(user_chats):
    def load_conversation(i: int):
        st.session_state["chat_history"] = user_chats["chats"][i]

    def delete_conversation(i: int):
        del user_chats["chats"][i]
        save_chats_to_file(st.session_state["chats"]["user"], user_chats)

    for i, item in enumerate(user_chats["chats"]):
        chat_tile_container = st.container()
        col_load, col_delete = st.columns(2)
        with chat_tile_container:
            if item:
                colored_header(
                    label=" ",
                    description=item["content"][1]["content"][:70],
                    color_name="blue-green-70"
                )
            col_load.button("Load", on_click=load_conversation, args=(i,), key=i)
            col_delete.button("Delete", on_click=delete_conversation, args=(i,), key=i+10000)


voice_enabled = False
with st.sidebar:
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


# @st.cache_resource
# def instantiate_model():
#     if st.session_state["model"] is None or st.session_state["model"] == "":
#         st.session_state["model"] = LLModel()

#     return st.session_state["model"]


url = "http://localhost:11434/api/generate"
api_url = "http://localhost:8000/text-to-speech"

headers = {
    'Content-Type': 'application/json',
}


def query_text_to_speech_api(text: str, lang: str = 'en'):
    try:
        # Sending a POST request
        data = {
            "text": text,
            "lang": lang
        }

        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:

            # Decode the binary data to a string
            json_string = response.content.decode('utf-8')
            # print(json_string)
            # Convert the JSON string to a Python list
            audio_list = json.loads(json_string)
            audio_array = np.array(audio_list)
            return audio_array
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        # Print an error message in case of an exception
        print(f"Exception: {str(e)}")


def generate_response(prompt):

    data = {
        "model": "mistral",
        "stream": False,
        "prompt": prompt,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data["response"]
        return actual_response
    else:
        print("Error:", response.status_code, response.text)
        return None


def process_query(query_str: str) -> None:

    if not query_str:
        st.error("Please enter a question.")
        return

    with st.status("I'm thinking...", expanded=False) as status:
        with text_area_container:
            final_prompt = query_str

            st.session_state["chat_history"]["content"].append({'role': 'user', 'content': final_prompt})
            response = generate_response(final_prompt)

            # Add output to chat history
            st.session_state["chat_history"]["content"].append({'role': 'assistant', 'content': response})
            quicksave_chat()
            save_chats_to_file(st.session_state["chats"]["user"], st.session_state["chats"])
            if voice_enabled:
                status.update(label="Weaving resonance...", state="running", expanded=False)
                return query_text_to_speech_api(text=response)
            else:
                return response


chat_container.empty()

with chat_container:
    for i, item in enumerate(st.session_state["chat_history"]["content"]):
        if i == 0:
            continue
        if item["role"] == 'assistant':
            with st.chat_message(item["role"], avatar='./tankfinal2.png'):
                st.markdown(item['content'])
        else:
            with st.chat_message(item["role"]):
                st.markdown(item['content'])


if query := st.chat_input("O Panzer of the Lake, what is your wisdom?"):
    st.chat_message('user').write(query)
    full_response = ""
    if voice_enabled:
        response_audio = process_query(query)
        with st.chat_message('ai', avatar='./tankfinal2.png'):
            st.write("The panzer speaks...")
            st.audio(response_audio, format='audio/wav', sample_rate=24000)
    else:
        response_text = process_query(query)
        st.chat_message('ai', avatar='./tankfinal2.png').write(response_text)
        st.write("Total tokens:", st.session_state["total_tokens_used"])
