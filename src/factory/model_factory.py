from models.azure_cohere_model import CohereAzureModel
from models.azure_openai_model import AzureOpenAIModel
from models.generic_https_model import GenericHttpsModel
from models.togetherai_model import TogetherAIModel
from models.ollama_model import OllamaModel
from models.open_ai_model import OpenAIModel
from models.transformers_model import TransformersModel
from interfaces.base_model import BaseModel
from typing import Optional
import streamlit as st


class ModelFactory:
    @classmethod
    def get_model(cls, model_provider: str, model_name: str, model_path: Optional[str] = None) -> BaseModel:
        if model_provider == "Azure":
            return AzureOpenAIModel(
                api_key=st.secrets["AZURE_OPENAI_API_KEY"],
                api_version=st.secrets["AZURE_API_VERSION"],
                azure_endpoint=st.secrets["AZURE_OPENAI_BASE"],
                model_name=model_name,
                default_headers={"Ocp-Apim-Subscription-Key": st.secrets["AZURE_OPENAI_API_KEY"]},
            )
        elif model_provider == "Cohere":
            return CohereAzureModel(
                api_key=st.secrets["AZURE_COHERE_API_KEY"],
                api_version=st.secrets["AZURE_API_VERSION"],
                azure_endpoint=st.secrets["AZURE_COHERE_BASE"],
                model_name=model_name,
            )
        elif model_provider == "OpenAI":
            return OpenAIModel(
                api_key=st.secrets["OPENAI_API_KEY"],
                model_name=model_name,
            )
        elif model_provider == "TogetherAI":
            return TogetherAIModel(
                api_key=st.secrets["TOGETHER_AI_API_KEY"],
                base_url=st.secrets["TOGETHER_AI_BASE"],
                model_name=model_name,
            )
        elif model_provider == "Ollama":
            return OllamaModel(
                endpoint=st.secrets["OLLAMA_BASE"],
                model_name=model_name,
            )
        elif model_provider == "Transformers":
            return TransformersModel(model_path)
        else:
            raise ValueError("Invalid Model Provider")
