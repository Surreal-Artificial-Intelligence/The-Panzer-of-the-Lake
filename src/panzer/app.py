import streamlit as st

from web.config import (
    ASSETS_PATH,
    LOGO_CONFIG,
)

st.set_page_config(
    page_title="POTL",
    page_icon=f"{ASSETS_PATH}/surreal-logo.jpg",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"},
)
st.logo(**LOGO_CONFIG)

customize_section = [
    st.Page(
        "web/manuscripts/prompt_template_editor.py",
        title="Prompt Template Editor",
        icon=":material/edit_note:",
    ),
    st.Page(
        "web/manuscripts/models_info.py",
        title="Models",
        icon=":material/book_2:",
    ),
]

generate_section = [
    st.Page(
        "web/manuscripts/home.py",
        title="Chat",
        icon=":material/chat:",
    ),
    st.Page(
        "web/manuscripts/images.py",
        title="Image",
        icon=":material/image:",
    ),
    st.Page(
        "web/manuscripts/transcribe.py",
        title="Speech",
        icon=":material/mic:",
    ),
]


pg = st.navigation({"Generate": generate_section, "Customize": customize_section})
pg.run()
