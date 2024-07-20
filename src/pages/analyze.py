import os

import streamlit as st
from streamlit_extras.colored_header import colored_header

from config import (
    ASSETS_PATH,
    LOGO_CONFIG,
)


# Streamlit Page Configuration
st.set_page_config(
    page_title="Token Counter",
    page_icon=f"{ASSETS_PATH}/surreal-logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"about": "Built by Surreal AI"},
)


colored_header(
    label="Artifact Analyzer", description="Give me the docs", color_name="red-70"
)

st.logo(**LOGO_CONFIG)


@st.cache_data
def set_session_variables() -> None:
    pass


set_session_variables()

# Utility Functions
# UI Containers

file = st.file_uploader("Upload a file", type=["csv", "txt", "pdf"])
submit = st.button("Send")
if submit:
    if file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()

        if file.type == "text/csv":
            loader = CSVLoader(file_path="./example_data/mlb_teams_2012.csv")
            data = loader.load()

            doc = "csv"
            data = load_csv_data(file)
            agent = create_csv_agent(
                OpenAI(temperature=0), "uploaded_file.csv", verbose=True
            )
            st.dataframe(data)

        elif file.type == "text/plain":
            doc = "text"
            data = load_txt_data(file)
            loader = TextLoader("uploaded_file.txt")
            index = VectorstoreIndexCreator().from_loaders([loader])

        elif file.type == "application/pdf":
            doc = "text"
            loader = PyPDFLoader(file)
            pages = loader.load_and_split()
