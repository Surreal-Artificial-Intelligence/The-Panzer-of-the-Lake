import streamlit as st
from streamlit_extras.colored_header import colored_header

from factory.model_factory import ModelFactory
from data_class.model_response import ModelResponse
from interfaces.base_model import BaseModel
from tinydb_access import TinyDBAccess
from models.togetherai_model import TogetherAIModel

from config import (
    ASSETS_PATH,
    LOGO_CONFIG,
    SUPPORTED_IMAGE_MODELS,
)

colored_header(
    label="Panzer of the Sky",
    description="Ask the sky for an image and it may grant it",
    color_name="blue-green-70",
)

def set_session_variables() -> None:
    """Set the session chat and output, containers."""
    if "containers" not in st.session_state:
        st.session_state["containers"] = {}


set_session_variables()


with st.sidebar:
    model_provider = st.selectbox("Provider:", SUPPORTED_IMAGE_MODELS.keys()) or "Ollama"
    model_name = st.selectbox("Model:", SUPPORTED_IMAGE_MODELS[model_provider]) or "Ollama"


@st.cache_resource
def get_model_client(model_provider: str, model_label: str) -> BaseModel:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    model_client = model_factory.get_model(model_provider, model_label)
    return model_client


# TODO: Save images to DB


def generate_image(image_prompt: str):
    """Generate image from prompt using model. Returns a URL"""
    client = get_model_client(model_provider, model_name)

    # satisfy type checker
    if isinstance(client, TogetherAIModel):
        response = client.image(prompt=image_prompt)
    else:
        raise TypeError(f"Expected a {TogetherAIModel} instance, but received a {type(client)}")

    return str(response.data[0].url)


prompt = st.text_input("An image prompt")

confirm = st.button("Generate", icon=":material/circle:")
if confirm and prompt:
    with st.status("I'm thinking...", expanded=False) as status:
        image = generate_image(prompt)

    st.image(image=image, caption=prompt)
