import streamlit as st

chat_page = st.Page(
    "home.py",
    title="Chat",
    icon=":material/chat:",
)

prompt_templates_page = st.Page(
    "manuscripts/prompt_template_editor.py",
    title="Prompt Template Editor",
    icon=":material/edit_note:",
)

image_page = st.Page(
    "manuscripts/images.py",
    title="Image Generator",
    icon=":material/image:",
)

pg = st.navigation({
    "Generate": [chat_page, image_page],
    "Customize":  [prompt_templates_page]
})
pg.run()
