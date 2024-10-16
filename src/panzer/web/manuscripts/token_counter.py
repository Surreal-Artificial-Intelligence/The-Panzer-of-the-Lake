import os

import streamlit as st
from streamlit_extras.colored_header import colored_header

from PIL import Image
import tiktoken

colored_header(
    label="Token Counter",
    description="Paste text here and I will tell you how big the oracle will consider it.",
    color_name="red-70",
)

# Utility Functions
output_container = st.container()
output_container.empty()

text_area_container = st.container()
text_area_container.empty()


# Session States
@st.cache_data
def set_session_variables() -> None:
    tiktoken_cache_dir = "cache/tiktoken_cache/"
    os.environ["TIKTOKEN_CACHE_DIR"] = tiktoken_cache_dir

    # validate
    assert os.path.exists(os.path.join(tiktoken_cache_dir, "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"))


if "count" not in st.session_state:
    st.session_state["count"] = 0

set_session_variables()

# Utility Functions
# UI Containers
with text_area_container:
    text = st.text_area("Enter text:", key="text")
    submit = st.button("Send")
    if submit:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens_integer = encoding.encode(text)
st.write("Total tokens used :", len(tokens_integer))
