from models.azure_cohere_model import CohereAzureModel
from models.azure_openai_model import AzureOpenAIModel
from models.generic_https_model import GenericHttpsModel
from models.ollama_model import OllamaModel
from models.open_ai_model import OpenAIModel
import streamlit as st


class ModelFactory:
    @classmethod
    def get_model(cls, model_provider: str, model_name: str):
        if model_provider == "azure":
            return AzureOpenAIModel(
                api_key=st.secrets["AZURE_OPENAI_API_KEY"],
                api_version=st.secrets["AZURE_API_VERSION"],
                azure_endpoint=st.secrets["AZURE_OPENAI_BASE"],
                model_name=model_name,
            )
        elif model_provider == "cohere":
            return CohereAzureModel(
                api_key=st.secrets["AZURE_COHERE_API_KEY"],
                api_version=st.secrets["AZURE_API_VERSION"],
                azure_endpoint=st.secrets["AZURE_COHERE_BASE"],
                model_name=model_name,
            )
        elif model_provider == "openai":
            return OpenAIModel(
                api_key=st.secrets["OPENAI_API_KEY"],
                model_name=model_name,
            )
        elif model_provider == "togetherai":
            return GenericHttpsModel(
                api_key=st.secrets["TOGETHER_AI_API_KEY"],
                api_version=st.secrets["AZURE_API_VERSION"],
                endpoint=st.secrets["TOGETHER_AI_BASE"],
                model_name=model_name,
            )
        else:
            return OllamaModel(
                endpoint=st.secrets["OLLAMA_BASE"],
                model_name=model_name,
            )
