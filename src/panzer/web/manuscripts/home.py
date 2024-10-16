import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_extras.colored_header import colored_header


from core.services.rag_manager import RAGManager
from core.services.document_engine import DocumentEngine

from core.factory.model_factory import ModelFactory
from core.models.responses.model_response import ModelResponse
from core.models.base_model import BaseModel
from data.tinydb_access import TinyDBAccess

from web.config import SUPPORTED_MODELS, ASSETS_PATH, CHATS_PATH, DB_PATH, SYSTEM_PROMPT

from web.utils import save_chats_to_file, load_data, encode_image


maincol1, maincol2 = st.columns((10, 3))

with maincol1:
    colored_header(
        label="Panzer of the Lake",
        description="Welcome to the lake ask your question so the Panzer may answer it.",
        color_name="blue-green-70",
    )
    chat_container = st.container()
    chat_container.empty()
    text_area_container = st.container()
    text_area_container.empty()

side_chats_container = st.container()
side_chats_container.empty()

with maincol2:
    other_sidebar_container = st.container()
    other_sidebar_container.empty()


@st.cache_resource
def get_model_client(model_provider: str, model_label: str) -> BaseModel:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    return model_factory.get_model(model_provider, model_label)


@st.cache_resource
def get_rag_manager(model_provider, model_label):
    model = get_model_client(model_provider, model_label)
    return RAGManager(model, DocumentEngine(500, 10))


@st.cache_resource
def get_tinydb_client(db_path: str) -> TinyDBAccess:
    """Instantiate and return the TinyDB access client"""
    client = TinyDBAccess(db_path)
    return client


def initialize_session_variables() -> None:
    """Initializes session variables and loads user data."""
    tinydb_client = get_tinydb_client(DB_PATH)

    if "DB_PATH" not in st.session_state:
        st.session_state["DB_PATH"] = DB_PATH

    if "user" not in st.session_state:
        st.session_state["user"] = "Emile"

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = {
            "title": "",
            "content": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                }
            ],
        }

    if "chats" not in st.session_state:
        st.session_state["chats"] = load_data("Emile", CHATS_PATH)

    if "templates" not in st.session_state:
        tinydb_client.initialize_database(st.session_state["user"])
        st.session_state["templates"] = tinydb_client.load_templates(st.session_state["user"])

    if "model" not in st.session_state:
        st.session_state["model"] = None

    if "total_tokens_used" not in st.session_state:
        st.session_state["total_tokens_used"] = 0

    if "file" not in st.session_state:
        st.session_state["file"] = {}

    if "hyperparameters" not in st.session_state:
        st.session_state["hyperparameters"] = {
            "temperature": 0.5,
            "top_p": 0.95,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
        }


initialize_session_variables()


def quicksave_chat():
    """
    Saves the current chat that is in chat history into the all user chats variable.
    Basically a quicksave function.
    """
    if st.session_state["chat_history"] not in st.session_state["chats"]["chats"]:
        st.session_state["chats"]["chats"].append(st.session_state["chat_history"])
    else:
        # overwrite existing one
        for i, item in enumerate(st.session_state["chats"]["chats"]):
            if item == st.session_state["chat_history"]:
                st.session_state["chats"]["chats"][i] = st.session_state["chat_history"]
                break


def reset_stats():
    """Sets chat statistics to zero"""
    st.session_state["total_tokens_used"] = 0


def render_chats():
    """Renders chats in bubbles in the UI"""
    chat_container.empty()
    with maincol1:
        with chat_container:
            for item in st.session_state["chat_history"]["content"][1:]:
                if item["role"] == "assistant":
                    with st.chat_message(item["role"], avatar=f"{ASSETS_PATH}/tank.jpeg"):
                        st.markdown(item["content"])
                else:
                    with st.chat_message(item["role"], avatar=f"{ASSETS_PATH}/soldier.jpg"):
                        st.markdown(item["content"])


def populate_chats(user_chats):
    """Loads conversation from file memory"""

    def load_conversation(i: int):
        st.session_state["chat_history"] = user_chats["chats"][i]
        render_chats()

    def delete_conversation(i: int):
        del user_chats["chats"][i]
        save_chats_to_file(st.session_state["chats"]["user"], user_chats)

    for i, item in enumerate(user_chats["chats"]):
        chat_tile_container = st.container()
        col_load, col_delete = st.columns((3, 1))
        with chat_tile_container:
            if item:
                colored_header(
                    label="",
                    description=item["content"][1]["content"][:70],
                    color_name="blue-green-70",
                )
                col_load.button(
                    "",
                    on_click=load_conversation,
                    args=(i,),
                    key=i,
                    use_container_width=True,
                    icon=":material/arrow_right_alt:",
                )
                col_delete.button(
                    "",
                    on_click=delete_conversation,
                    args=(i,),
                    key=i + 10000,
                    use_container_width=True,
                    icon=":material/delete:",
                )


def update_chat_history(chat_content: dict):
    """Appends new content to the chat history session variable"""
    st.session_state["chat_history"]["content"].append(chat_content)
    return


@st.dialog("Attach your media.")
def file_uploader():
    file = st.file_uploader("Upload your media.", type=["png", "jpg"], key="media")
    if file:
        bytes_data = file.getvalue()
        st.image(bytes_data, caption=file.name, use_column_width=True)

    confirm = st.button("Confirm")
    if confirm and file:
        encoded_image = encode_image(bytes_data)
        st.session_state["image"] = {"file_name": file.name, "content": encoded_image}
        st.rerun()


voice_enabled = False
with st.sidebar:
    model_provider = st.selectbox("Provider:", SUPPORTED_MODELS.keys()) or "Ollama"
    model_name = st.selectbox("Model:", SUPPORTED_MODELS[model_provider]) or "Ollama"
    template_name = st.selectbox("Prompt Template:", [item.name for item in st.session_state["templates"]])
    st.divider()
    voice_enabled = st.checkbox("Voice")

    hyperparameters_enabled = st.checkbox("Hyperparameters")
    if hyperparameters_enabled:
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        st.session_state["hyperparameters"] = {
            "temperature": temp,
        }
    st.divider()
    side_chats_container = st.container()
    side_chats_container.empty()
    with side_chats_container:
        populate_chats(st.session_state["chats"])


def evaluate_image(templated_message: str, image_type: str):
    if st.session_state["image"]["content"] and (model_provider in ["OpenAI", "Azure", "TogetherAI"]):
        message_data = {
            "role": "user",
            "content": [
                {"type": "text", "text": templated_message},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/{image_type};base64,{st.session_state['image']['content']}"},
                },
            ],
        }
        st.session_state["image"] = ""
    else:
        message_data = (
            {"role": "user", "content": templated_message}
            if st.session_state["image"]["content"] == ""
            else {"role": "user", "content": templated_message, "images": [st.session_state["image"]["content"]]}
        )
    return message_data


def validate_model_response(model_response: ModelResponse):
    if not model_response.usage or not model_response.message:
        raise ValueError(
            "Invalid model response: missing 'usage' or 'message'. Check what the specific model class is returning"
        )


def handle_model_response(model_response: ModelResponse):
    if model_response.usage["total_tokens"] == 0:
        st.error(model_response.message["content"])
    else:
        st.session_state["total_tokens_used"] = model_response.usage["total_tokens"]
        update_chat_history(model_response.message)

# TODO; make a streamlit agnostic implementation
def process_file(file: UploadedFile, tmessage: str) -> dict:
    """Process file based on type"""

    message_data = {}
    if file.type in ["image/png", "image/jpg"]:
        encoded_image = encode_image(file.getvalue())
        if model_provider in ["OpenAI", "Azure", "TogetherAI"]:
            message_data = {
                "role": "user",
                "content": [
                    {"type": "text", "text": tmessage},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{file.type.split('/')[1]};base64,{encoded_image}"},
                    },
                ],
            }
        else:
            message_data = (
                {"role": "user", "content": tmessage}
                if encoded_image == ""
                else {"role": "user", "content": tmessage, "images": [encoded_image]}
            )

    elif file.type in ["application/pdf"]:
        ragman = get_rag_manager(model_provider, model_name)
        # TODO: need to add passing in file
        ragman.process_document(file)

    st.session_state["file"] = ""
    return message_data


def process_query(query_string: str) -> str:
    """Handles user input"""
    working_chat_hist = {}
    with st.status("I'm thinking...", expanded=False) as status:
        with text_area_container:
            # TODO search by id or by direct db query
            selected_template = [t.text for t in st.session_state["templates"] if t.name == template_name][0]
            templated_message = selected_template.format(query_string)

            if st.session_state["file"]:
                message_data = process_file(st.session_state["file"], templated_message)

                # so that massive encodings don't destroy the db
                working_chat_hist = st.session_state["chat_history"]["content"].copy()
                working_chat_hist.append(message_data)

            update_chat_history({"role": "user", "content": templated_message})
            render_chats()

            client = get_model_client(model_provider, model_name)
            model_response = client.chat(working_chat_hist if working_chat_hist else st.session_state["chat_history"]["content"])
            validate_model_response(model_response)
            handle_model_response(model_response)

            quicksave_chat()
            save_chats_to_file(st.session_state["chats"]["user"], st.session_state["chats"])

            # if voice_enabled:
            #     status.update(label="Weaving resonance...", state="running", expanded=False)
            #     return query_text_to_speech_api(text=model_response.message["content"])
            # else:

            return model_response.message["content"]


with other_sidebar_container:
    file = st.file_uploader("upload", label_visibility="hidden", type=["png", "jpg", "pdf", "txt"])
    if file:
        st.session_state["file"] = file


if query := st.chat_input("O Panzer of the Lake, what is your wisdom?"):
    response = process_query(query)
    if voice_enabled:
        with st.chat_message("ai", avatar=f"{ASSETS_PATH}/tank.jpeg"):
            st.write("Hear ye, hear ye.")
            st.audio(response, format="audio/wav", sample_rate=24000)
    else:
        st.chat_message("ai", avatar=f"{ASSETS_PATH}/tank.jpeg").write(response)
        st.write("Total tokens:", st.session_state["total_tokens_used"])
