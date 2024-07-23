import streamlit as st
from streamlit_extras.colored_header import colored_header
from tinydb import TinyDB, Query
from data_class.prompt_template import PromptTemplate
from tinydb.table import Document
from config import LOGO_CONFIG, DB_PATH, ASSETS_PATH


st.set_page_config(
    page_title="POTL",
    page_icon=f"{ASSETS_PATH}/surreal-logo.jpg",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"about": "Built by Surreal AI"},
)

colored_header(
    label="Panzer Prompt Template Editor",
    description="Edit your prompt templates here to make asking the panzer the same questions easier.",
    color_name="blue-green-70",
)

st.logo(**LOGO_CONFIG)

# # @st.cache_resource

# def save_template():
#     """Saves the current template to the database"""
#     with db


def initialize_database(user: str):
    """Initialize the prompt template table."""

    with TinyDB(DB_PATH) as db:
        templates = [
            {"user": user, "name": "None", "text": "{}"},
            {
                "user": user,
                "name": "Summarize",
                "text": "Summarize the following text: {}",
            },
            {
                "user": user,
                "name": "Jokes",
                "text": "Give me jokes about the topic: {}",
            },
        ]

        table = db.table("prompt_template")

        existing_templates = table.search(
            (Query().name == "None") and (Query().user == user)
        )

        if existing_templates:
            return

        table.insert_multiple(templates)

    print("Prompt templates initialized.")


def init_session_states() -> None:
    """Initializes session variables"""

    if "user" not in st.session_state:
        st.session_state["user"] = "Emile"

    if "edit" not in st.session_state:
        st.session_state["edit"] = ""

    if "user_templates" not in st.session_state:
        initialize_database(st.session_state["user"])
        with TinyDB(DB_PATH) as db:
            results = db.table("prompt_template").search(
                Query().user == st.session_state["user"]
            )
            # need to iterate to get doc_id
            documents_with_ids = [
                PromptTemplate(id=doc.doc_id, name=doc["name"], text=doc["text"])
                for doc in results
            ]
            st.session_state["user_templates"] = documents_with_ids


template_list_column, edit_template_column = st.columns(2)

init_session_states()


def load_templates(user: str):
    st.session_state["user_templates"] = (
        TinyDB(DB_PATH).table("prompt_templates").search((Query().user == user))
    )


def upsert_template(template: PromptTemplate):
    """Updates or creates a template in the database."""

    with TinyDB(DB_PATH) as db:
        if template.id is None:

            db.table("prompt_template").insert(
                {
                    "user": st.session_state["user"],
                    "name": template.name,
                    "text": template.text,
                }
            )
            st.toast(f"Saved {template.name}", icon=":material/article:")
        else:
            db.table("prompt_template").upsert(
                Document(
                    {"name": template.name, "text": template.text}, doc_id=template.id
                )
            )
            st.toast(f"Updated {template.name}", icon=":material/ink_pen:")


def render_template():
    return


# def save_prompts_to_file(templates):
#     """Write templates to file"""
#     # TODO can this become completely universal for prompts and chats within the utils
#     # TODO surround in try catch
#     with open(f"{TEMPLATE_PATH}/{templates['user']}.json", "w", encoding=ENCODING) as f:
#         f.write(json.dumps(templates))


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
    title = st.text_input(
        "Title", value=st.session_state["edit"].name if st.session_state["edit"] else ""
    )
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
        upsert_template(
            PromptTemplate(None, name=new_template["name"], text=new_template["text"])
        )

    if update:
        updated_template = {
            "id": st.session_state["edit"].id,
            "name": title,
            "text": body,
        }
        upsert_template(PromptTemplate(**updated_template))
