import json

import streamlit as st
from streamlit_extras.colored_header import colored_header
from openai import AzureOpenAI


# Streamlit Page Configuration
st.set_page_config(
    page_title="Panzer of the Sky",
    page_icon="cloud",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"about": "Built by Surreal AI"})

colored_header(label="Panzer of the Sky",
               description="Ask the sky for an image and it may grant it",
               color_name="blue-70", )


# Session States
def set_session_variables() -> None:
    """ Set the session chat and output, containers. """
    if 'containers' not in st.session_state:
        st.session_state["containers"] = {}


set_session_variables()


@st.cache_resource
def get_openai_azure_connection():
    """Instantiate and return the AzureOpenAI model client"""
    client = AzureOpenAI(api_key=st.secrets['AZURE_OPENAI_API_KEY'],
                         api_version=st.secrets['AZURE_API_VERSION'],
                         azure_endpoint=st.secrets['AZURE_OPENAI_BASE']
                         )
    return client


def generate_image(image_prompt: str, model: str = "Dalle3"):
    """Generate image from prompt using model"""
    client = get_openai_azure_connection()
    result = client.images.generate(
        model=model,
        prompt=image_prompt,
        n=1
    )
    return json.loads(result.model_dump_json())['data'][0]['url']


image_prompt = st.text_input("An image prompt")
button = st.button("Generate")
if button:
    image_link = generate_image(image_prompt)
    st.image(image=image_link, caption=image_prompt)
