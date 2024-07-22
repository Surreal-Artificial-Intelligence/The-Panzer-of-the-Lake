import os
import time
import random, re

import streamlit as st
from streamlit_extras.colored_header import colored_header

import requests

from bs4 import BeautifulSoup

from config import (
    SUPPORTED_MODELS,
    ASSETS_PATH,
    CHATS_PATH,
    TEMPLATES_PATH,
    LOGO_CONFIG,
)


st.set_page_config(
    page_title="Summarizer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"about": "Built by Surreal AI"},
)

colored_header(
    label="Panzer of the lake",
    description="Ms Minutes summarizes web pages so that you can absorb information and move on to what matters.",
    color_name="orange-70",
)

chat_container = st.container()
chat_container.empty()
text_area_container = st.container()
text_area_container.empty()

button_container = st.container()
button_container.empty()


# Session States
def set_session_variables() -> None:
    """Set the session chat and output, containers."""
    if "containers" not in st.session_state:
        st.session_state["containers"] = {}


set_session_variables()

with st.sidebar:
    side_chats_container = st.container()
    side_chats_container.empty()

hyp = st.checkbox("Hyperparameters")
if hyp:
    st.markdown("# Hyperparameters")
    temp = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
    max_t = st.number_input("Max Tokens", 0, 15000, 800, 10)
    top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.01)
    f_pen = st.slider("Frequency Penalty", 0.0, 2.0, 0.0, 0.1)
    p_pen = st.slider("Presence Penalty", 0.0, 2.0, 0.0, 0.1)
else:
    temp = 0.5
    max_t = 5000
    top_p = 0.95
    f_pen = 0.0
    p_pen = 0.0
hyperparameters = {
    "temp": temp,
    "max_t": max_t,
    "top_p": top_p,
    "f_pen": f_pen,
    "p_pen": p_pen,
}


# Utility Functions
def remove_newlines(input_string):
    return re.sub(r"\n{3,}", "\n\n", input_string)


def process_query(url_str: str) -> None:
    if not url_str:
        st.error("Please enter a URL.")
        return
    with text_area_container:
        with st.spinner("Wait for it..."):
            response = requests.get(url_str)
            soup = BeautifulSoup(response.text, "html.parser")
            page_content = remove_newlines(soup.get_text())
            template = """Summarize the <text> according to its headings, i.e., perform a summary per heading of the text, format your summary in markdown where it makes sense. Make the summary verbose but still captures only facts: <text> {text} </text> Summary: """
            # st.session_state["chat_history"] = [{'role': 'system', 'content': 'You are an AI assistant'}]
            # st.session_state["chat_history"].append({'role': 'user', 'content': template.format(text=page_content)})
            # st.markdown(continue_conversation(st.session_state["chat_history"], on_retry=log_retries, temperature=hyperparameters['temp'], max_tokens=hyperparameters['max_t'], top_p=hyperparameters['top_p'], frequency_penalty=hyperparameters['f_pen'], presence_penalty=hyperparameters['p_pen'] ))


st.markdown("""---""")
st.write("Total tokens used :", st.session_state["total_tokens_used"])

chat_container.empty()
with chat_container:
    chat_container.empty()

with text_area_container:
    query = st.text_input("URL:", key="url")
    submit = st.button("Summarize", on_click=process_query, args=(query,))
