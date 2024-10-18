import streamlit as st
from streamlit_extras.colored_header import colored_header
import json

from core.factory.model_factory import ModelFactory
from core.models.responses.model_response import ModelResponse
from core.models.base_model import BaseModel
from data.tinydb_access import TinyDBAccess
from core.models.transformers_model import TransformersModel


colored_header(
    label="Panzer of the Library",
    description="Welcome to the archives, give the panzer your voice so it may scribe it.",
    color_name="blue-green-70",
)


def initialize_session_variables() -> None:
    """Initializes session variables and loads user data."""

    if "result" not in st.session_state:
        st.session_state["result"] = ""


initialize_session_variables()


# @st.cache_resource
def get_model_client(model_provider: str, model_label: str) -> BaseModel:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    model_client = model_factory.get_model(model_provider, model_label)
    return model_client


# @st.cache_resource
# def load_model(transformer_model_client: TransformersModel) -> TransformersModel:
#     return transformer_model_client.load_model(model_id="openai/whisper-large-v3")


file = st.file_uploader("Upload your media.", type=["mp3", "mp4", "wav", "opus"], key="media")
if file:
    bytes_data = file.getvalue()

# TODO: Add history for transcriptions - connect to tiny DB

confirm = st.button("Transcribe")
if confirm and file:
    with st.status("I'm thinking...", expanded=False) as status:
        transformer_model_client = get_model_client(model_provider="Transformers", model_label="whisper-v3-large")
        status.update(label="Loading model...", state="running", expanded=False)

        # satisfy type checker
        if isinstance(transformer_model_client, TransformersModel):
            transformer_model_client.load_model(model_id="openai/whisper-large-v3")
        else:
            raise TypeError(f"Expected a {TransformersModel} instance, but received a {type(transformer_model_client)}")

        status.update(label="Running inference...", state="running", expanded=False)
        result: dict = transformer_model_client.transcribe(bytes_data, "")
        st.session_state["result"] = result["text"]

    st.session_state["result"]
    st.audio(bytes_data)
