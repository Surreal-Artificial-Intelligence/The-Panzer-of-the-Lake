import streamlit as st
from streamlit_extras.colored_header import colored_header
from shared.data_class.prompt_template import PromptTemplate

from web.config import DB_PATH
from data.tinydb_access import TinyDBAccess


colored_header(
    label="Panzer Prompt Template Editor",
    description="Edit your prompt templates here to make asking the panzer the same questions easier.",
    color_name="blue-green-70",
)


@st.cache_resource
def get_tinydb_client(db_path: str) -> TinyDBAccess:
    """Instantiate and return the TinyDB access client"""
    client = TinyDBAccess(db_path)
    return client


tinydb_client = get_tinydb_client(DB_PATH)


def refresh_session_templates():
    st.session_state["user_templates"] = tinydb_client.load_templates(st.session_state["user"])


def init_session_states() -> None:
    """Initializes session variables"""

    if "user" not in st.session_state:
        st.session_state["user"] = "Emile"

    if "edit" not in st.session_state:
        st.session_state["edit"] = ""

    if "user_templates" not in st.session_state:
        tinydb_client.initialize_database(st.session_state["user"])
        refresh_session_templates()


template_list_column, edit_template_column = st.columns(2)

init_session_states()


def populate_template():
    """Renders templates in bubbles in the UI"""

    def load_template(id: int):
        """Finds and loads a template from the session state into the editor"""
        for pt in st.session_state["user_templates"]:
            if pt.id == id:
                st.session_state["edit"] = pt
                break

    def delete_template(i: int):
        pass

    for i, prompt_template in enumerate(st.session_state["user_templates"]):
        template_tile_container = st.container()
        col_load, col_delete = st.columns(2)
        if prompt_template.name == "None":
            continue

        with template_tile_container:
            colored_header(
                label="",
                description=f"## {prompt_template.name} \n\n {prompt_template.name}",
                color_name="blue-green-70",
            )
            col_load.button(
                "Load",
                on_click=load_template,
                args=(prompt_template.id,),
                key=i,
                use_container_width=True,
            )
            col_delete.button(
                "🗑",
                on_click=delete_template,
                args=(prompt_template.id,),
                key=i + 10000,
                use_container_width=True,
            )


with st.sidebar:
    side_container = st.container()
    side_container.empty()
    with side_container:
        populate_template()

with edit_template_column:
    title = st.text_input("Title", value=st.session_state["edit"].name if st.session_state["edit"] else "")
    body = st.text_area(
        value=st.session_state["edit"].text if st.session_state["edit"] else "",
        label="Template (remember the {})",
        height=500,
        placeholder="Click on a template to edit it...",
    )
    col1, col2 = st.columns(2)
    with col1:
        update = st.button("Update")
    with col2:
        create = st.button("Create")

    if create:
        new_template = {
            "name": title,
            "text": body,
        }
        tinydb_client.upsert_prompt_template(
            st.session_state["user"], PromptTemplate(None, name=new_template["name"], text=new_template["text"])
        )
        st.toast(f"Saved {title}", icon=":material/article:")
        refresh_session_templates()

    if update:
        updated_template = {
            "id": st.session_state["edit"].id,
            "name": title,
            "text": body,
        }
        tinydb_client.upsert_prompt_template(st.session_state["user"], PromptTemplate(**updated_template))
        st.toast(f"Updated {title}", icon=":material/ink_pen:")
        refresh_session_templates()
