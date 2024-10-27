import streamlit as st
from streamlit_extras.card import card
from streamlit_extras.colored_header import colored_header
from dataclasses import dataclass
from typing import List, Dict, Optional
from core.factory.model_factory import ModelFactory
from core.models.base_model_client import BaseModelClient
from shared.data_class.aimodel import AIModel

from web.config import (
    SUPPORTED_MODELS
)

colored_header(
    label="Models",
    description="Check out all the models that the panzer offers",
    color_name="blue-green-70",
)


def set_session_variables() -> None:
    """Set the session chat and output, containers."""
    if "containers" not in st.session_state:
        st.session_state["containers"] = {}
    if "models" not in st.session_state:
        st.session_state["models"] = {}


set_session_variables()


@st.cache_resource
def get_model_client(model_provider: str) -> BaseModelClient:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    return model_factory.get_model(model_provider)

# TODO: have a dropdown list for providers that when selected calls the list method for a specific model provider
# and then shows all availble model as cards. Also be able to set preference of main model for the chat page

def model_card(model: AIModel):
    col1, col2 = st.columns((5, 3))
    with col1:
        st.metric(label=model.organization, value=model.display_name, delta=f"${model.price_input:.2f}/mil - ${model.price_output:.2f}/mil ", delta_color="off")
    with col2:
        st.metric(label=str(model.license) if model.license else "NA", value=str(model.context_length), delta_color="off")
    st.divider()
model_provider = st.selectbox("Provider:", SUPPORTED_MODELS.keys()) or "Ollama"

getm = st.button("Get Models")
if getm:
    model_client = get_model_client(model_provider)
    st.session_state["models"] = model_client.models()
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Chat", "Image", "Embedding", "Code", "Language", "Moderation", "Rerank"]
    )
    for model in st.session_state["models"]:
        if model.type == "chat":
            with tab1:
                model_card(model)
        elif model.type == "image":
            with tab2:
                model_card(model)
        elif model.type == "embedding":
            with tab3:
                model_card(model)
        elif model.type == "code":
            with tab4:
                model_card(model)
        elif model.type == "language":
            with tab5:
                model_card(model)
        elif model.type == "moderation":
            with tab6:
                model_card(model)
        elif model.type == "rerank":
            with tab7:
                model_card(model)
        else:
            print(model)
