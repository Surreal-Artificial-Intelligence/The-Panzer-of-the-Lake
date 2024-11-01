from core.models.azure_cohere_model import CohereAzureModel
from core.models.azure_openai_model import AzureOpenAIModel
from core.models.togetherai_model import TogetherAIModel
from core.models.ollama_model import OllamaModel
from core.models.open_ai_model import OpenAIModel
from core.models.transformers_model import TransformersModel
from core.models.base_model_client import BaseModelClient
from typing import Optional
import streamlit as st
# TODO: Add debugging mode flag, also add logger


class ModelFactory:
    @staticmethod
    def get_model(model_provider: str, model_path: Optional[str] = None) -> BaseModelClient:
        match model_provider:
            case "Azure":
                return AzureOpenAIModel(
                    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
                    api_version=st.secrets["AZURE_API_VERSION"],
                    azure_endpoint=st.secrets["AZURE_OPENAI_BASE"],
                    image_endpoint=st.secrets.get("AZURE_IMAGE_ENDPOINT_BASE", None),
                    default_headers={"Ocp-Apim-Subscription-Key": st.secrets["AZURE_OPENAI_API_KEY"]},
                )
            case "Cohere":
                return CohereAzureModel(
                    api_key=st.secrets["AZURE_COHERE_API_KEY"],
                    api_version=st.secrets["AZURE_API_VERSION"],
                    azure_endpoint=st.secrets["AZURE_COHERE_BASE"],
                )
            case "OpenAI":
                return OpenAIModel(
                    api_key=st.secrets["OPENAI_API_KEY"],
                )
            case "TogetherAI":
                return TogetherAIModel(
                    api_key=st.secrets["TOGETHER_AI_API_KEY"],
                    base_url=st.secrets["TOGETHER_AI_BASE"],
                )
            case "Ollama":
                return OllamaModel(
                    endpoint=st.secrets["OLLAMA_BASE"],
                )
            case "Transformers":
                return TransformersModel()
        # elif model_provider == "Coqui":
        # return CoquiTTSModel()
            case _:
                raise ValueError("Invalid Model Provider")
