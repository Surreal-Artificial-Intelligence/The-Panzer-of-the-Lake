import json

import streamlit as st
from streamlit_extras.colored_header import colored_header

from st_utils import (
    ENCODING,
    load_data
)

TEMPLATES_PATH = "./templates"

st.set_page_config(
    page_title="POTL",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"}
)

colored_header(label="Panzer Prompt Template Editor",
               description="Edit your prompt templates here to make asking the panzer the same questions easier.",
               color_name="blue-green-90"
               )


def initialize_session_variables() -> None:
    """Initializes session variables"""

    if 'templates' not in st.session_state:
        st.session_state["templates"] = load_data("Emile", TEMPLATES_PATH)["templates"]
        st.session_state["templates"] = st.session_state["templates"]["templates"]
    if 'i_template' not in st.session_state:
        st.session_state["i_template"] = ""


template_list_column, edit_template_column = st.columns(2)

initialize_session_variables()


def update_template():
    return


def render_template():

    return


def save_prompts_to_file(templates):
    '''Write templates to file'''
    # TODO can this become completely universal for prompts and chats within the utils
    # TODO surround in try catch
    with open(f"{TEMPLATE_PATH}/{templates['user']}.json", "w", encoding=ENCODING) as f:
        f.write(json.dumps(templates))


def populate_template():
    """Renders templates in bubbles in the UI"""
    def load_template(i: int):
        st.session_state["i_template"] = st.session_state["templates"][i]

    def delete_template(i: int):
        st.session_state["i_template"] = st.session_state["templates"][i]
        render_template()
        del st.session_state["templates"][i]
        save_prompts_to_file(st.session_state["templates"])

    for i, item in enumerate(st.session_state["templates"]):
        template_tile_container = st.container()
        col_load, col_delete = st.columns(2)
        with template_tile_container:
            if item:
                colored_header(
                    label="",
                    description=f"## {item['name']} \n\n {item['text']}",
                    color_name="yellow-10"
                )
                col_load.button("Load", on_click=load_template, args=(i,), key=i, use_container_width=True)
                col_delete.button("🗑", on_click=delete_template, args=(i,), key=i+10000, use_container_width=True)


with st.sidebar:
    side_container = st.container()
    side_container.empty()
    with side_container:
        populate_template()

with edit_template_column:
    title = st.text_input("Title", value=st.session_state["i_template"]["name"])
    body = st.text_area(value=st.session_state["i_template"]["text"], label="Template (remember the {})",
                        height=500, placeholder="Click on a template to edit it...")
    update = st.button("Update")
    if update:
        updated_template = {"name": title, "template": body}
        # st.session_state["i_template"] = 
        update_template()
