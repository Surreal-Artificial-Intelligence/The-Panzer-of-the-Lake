import streamlit as st
from streamlit_extras.colored_header import colored_header

from factory.model_factory import ModelFactory
from data_class.model_response import ModelResponse
from interfaces.base_model import BaseModel
from tinydb_access import TinyDBAccess
from models.transformers_model import TransformersModel

from config import (
    SUPPORTED_MODELS,
    ASSETS_PATH,
    CHATS_PATH,
    LOGO_CONFIG,
    DB_PATH,
)

from utils import save_chats_to_file, load_data, log_retries, encode_image

st.set_page_config(
    page_title="POTL",
    page_icon=f"{ASSETS_PATH}/surreal-logo.jpg",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"},
)

colored_header(
    label="Panzer of the Library",
    description="Welcome to the archives, give the panzer your voice so it may scribe it.",
    color_name="blue-green-70",
)


st.logo(**LOGO_CONFIG)


def initialize_session_variables() -> None:
    """Initializes session variables and loads user data."""

    if "result" not in st.session_state:
        st.session_state["result"] = ""


initialize_session_variables()


@st.cache_resource
def get_model_client(model_provider: str, model_label: str) -> BaseModel:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    return model_factory.get_model(model_provider, model_label)


# @st.cache_resource
# def load_model(transformer_model_client: TransformersModel) -> TransformersModel:
#     return transformer_model_client.load_model(model_id="openai/whisper-large-v3")


file = st.file_uploader("Upload your media.", type=["mp3", "mp4", "wav", "opus"], key="media")
if file:
    bytes_data = file.getvalue()

confirm = st.button("Confirm")
if confirm and file:
    with st.status("I'm thinking...", expanded=False) as status:
        transformer_model_client: TransformersModel = get_model_client(
            model_provider="Transformers", model_label="whisper-v3-large"
        )
        status.update(label="Loading model...", state="running", expanded=False)
        transformer_model_client.load_model(model_id="openai/whisper-large-v3")
        status.update(label="Running inference...", state="running", expanded=False)
        result = transformer_model_client.transcribe(bytes_data, "")
        st.session_state["result"] = result


st.session_state["result"]