import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_extras.colored_header import colored_header
from datetime import datetime


from core.services.rag.rag_manager import RAGManager
from core.services.rag.document_engine import DocumentEngine

from core.factory.model_factory import ModelFactory
from core.models.responses.model_response import ModelResponse
from core.models.base_model_client import BaseModelClient
from data.tinydb_access import TinyDBAccess
from shared.data_class.chat_user import ChatUser
from shared.data_class.chat_thread import ChatThread
from shared.data_class.chat_message import ChatMessage

from web.config import SUPPORTED_MODELS, ASSETS_PATH, DB_PATH, SYSTEM_PROMPT

from web.utils import encode_image


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
def get_model_client(model_provider: str) -> BaseModelClient:
    """Instantiate and return the model client using the ModelFactory"""
    model_factory = ModelFactory()
    return model_factory.get_model(model_provider)


@st.cache_resource
def get_rag_manager(model_provider: str):
    model = get_model_client(model_provider)
    return RAGManager(model, DocumentEngine(500, 10))


@st.cache_resource
def get_tinydb_client(db_path: str) -> TinyDBAccess:
    """Instantiate and return the TinyDB access client"""
    client = TinyDBAccess(db_path)
    return client

tinydb_client = get_tinydb_client(DB_PATH)

def initialize_session_variables() -> None:
    """Initializes session variables and loads user data."""

    if "DB_PATH" not in st.session_state:
        st.session_state["DB_PATH"] = DB_PATH

    if "user" not in st.session_state:
        st.session_state["user"] = "Emile"

    tinydb_client.initialize_database(st.session_state["user"])

    if "user_chats" not in st.session_state:
        st.session_state["user_chats"] = tinydb_client.load_chat_user(st.session_state["user"])

    if "chat_thread" not in st.session_state:
        st.session_state["chat_thread"] = ChatThread(
            title="", created_date=str(datetime.now()), usage=0, messages=[ChatMessage("system", SYSTEM_PROMPT.format(st.session_state["user"]))]
        )

    if "templates" not in st.session_state:
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


def update_chat_user():
    """
    Saves the current thread into the chat-user object
    A quicksave function.
    """
    if st.session_state["chat_thread"] not in st.session_state["user_chats"].chats:
        st.session_state["user_chats"].chats.append(st.session_state["chat_thread"])
    else:
        # overwrite existing one
        for i, item in enumerate(st.session_state["user_chats"].chats):
            if item == st.session_state["chat_thread"]:
                st.session_state["user_chats"].chats[i] = st.session_state["chat_thread"]
                break


def render_chats(chat_thread: ChatThread):
    """Renders chats in bubbles in the UI"""
    chat_container.empty()
    with maincol1:
        with chat_container:
            for item in chat_thread.messages[1:]:
                if item.role == "assistant":
                    with st.chat_message(item.role, avatar=f"{ASSETS_PATH}/tank.jpeg"):
                        st.markdown(item.content)
                else:
                    with st.chat_message(item.role, avatar=f"{ASSETS_PATH}/soldier.jpg"):
                        st.markdown(item.content)


def populate_chats(user_chats: ChatUser):
    """Loads conversation from file memory"""
    def load_conversation(i: int):
        st.session_state["chat_thread"] = user_chats.chats[i]
        render_chats(st.session_state["chat_thread"])

    def delete_conversation(i: int):
        del user_chats.chats[i]
        tinydb_client.upsert_chat_user(user_chats)

    for i, chat_thread in enumerate(user_chats.chats):
        chat_tile_container = st.container()
        col_delete, colspace, col_load = st.columns((1, 2, 1))
        with chat_tile_container:
            if chat_thread:
                colored_header(
                    label="",
                    description=chat_thread.messages[1].content[:70],
                    color_name="blue-green-70",
                )
                col_load.button(
                    "",
                    on_click=load_conversation,
                    args=(i,),
                    key=i,
                    help="Load thread",
                    use_container_width=True,
                    icon=":material/arrow_right_alt:",
                )
                col_delete.button(
                    "",
                    on_click=delete_conversation,
                    args=(i,),
                    key=i + 10000,
                    help="Delete thread",
                    use_container_width=True,
                    icon=":material/delete:",
                )




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
    voice_enabled = st.toggle("Voice Mode")
    hyperparameters_enabled = st.toggle("Hyperparameters")
    if hyperparameters_enabled:
        temp = st.slider("Temperature", 0.0, 1.0, 0.5, 0.1)
        st.session_state["hyperparameters"] = {
            "temperature": temp,
        }
    st.divider()
    side_chats_container = st.container()
    side_chats_container.empty()
    with side_chats_container:
        populate_chats(st.session_state["user_chats"])


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



def handle_model_response(model_response: ModelResponse):
    if not model_response.usage or not model_response.message:
        raise ValueError(
            "Invalid model response: missing 'usage' or 'message'. Check what the specific model class is returning"
        )

    if model_response.usage["total_tokens"] == 0:
        st.error(model_response.message["content"])
    else:
        st.session_state["total_tokens_used"] = model_response.usage["total_tokens"]
        update_conversation(ChatMessage(role=model_response.message["role"], content=model_response.message["content"],))


def update_conversation(chat_content: ChatMessage):
    """Appends new content to the chat_user session object for both assistant and user roles"""
    st.session_state["chat_thread"].messages.append(chat_content)
    return


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
        ragman = get_rag_manager(model_provider)
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
                working_chat_hist = st.session_state["chat_thread"].messages.copy()
                working_chat_hist.append(message_data)

            update_conversation(ChatMessage(role="user", content=templated_message))
            render_chats(st.session_state["chat_thread"])
            client = get_model_client(model_provider)
            chats = working_chat_hist if working_chat_hist else st.session_state["chat_thread"].messages_to_dict()
            model_response = client.chat(model_name, chats)
            handle_model_response(model_response)

            update_chat_user() # update local chat user
            tinydb_client.upsert_chat_user(st.session_state["user_chats"])

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
