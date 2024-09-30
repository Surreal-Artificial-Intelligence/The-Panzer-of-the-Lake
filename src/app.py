import streamlit as st


prompt_templates_page = st.Page(
    "manuscripts/prompt_template_editor.py",
    title="Prompt Template Editor",
    icon=":material/edit_note:",
)

generate = [
    st.Page(
        "home.py",
        title="Chat",
        icon=":material/chat:",
    ),
    st.Page(
        "manuscripts/images.py",
        title="Image Generator",
        icon=":material/image:",
    ),
    st.Page(
        "manuscripts/transcribe.py",
        title="Speech-to-Text",
        icon=":material/mic:",
    ),
]


pg = st.navigation({"Generate": generate, "Customize": [prompt_templates_page]})
pg.run()
