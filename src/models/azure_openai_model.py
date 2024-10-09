import numpy as np
import streamlit as st
from openai import AzureOpenAI
from interfaces.base_model import BaseModel
from data_class.model_response import ModelResponse
from data_class.image_response import ImageResponse
from data_class.embedding_response import EmbeddingResponse
from typing import Optional


class AzureOpenAIModel(BaseModel):
    """Azure OpenAI Model class. This class is a wrapper around the Azure OpenAI API. It provides methods for sending
    messages to the model, and retrieving responses from it. It also provides methods for logging retries and sleeping
    before retrying. The class is initialized with an Azure OpenAI API key, version, endpoint, and model name.
    """

    def __init__(
        self,
        api_key: str,
        api_version: str,
        model_name: str,
        azure_endpoint: str,
        image_endpoint: Optional[str] = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint
        self.client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint, **kwargs)
        self.model_name = model_name

        self.default_headers = kwargs.get("default_headers", {})

        self.image_endpoint = image_endpoint
        self.image_client = None

    def _initialize_image_client(self):
        if self.image_client is None:
            if not self.image_endpoint:
                raise ValueError("Azure OpenAI image endpoint is required")
            self.image_client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.image_endpoint,
                default_headers=self.default_headers,
            )

    def chat(
        self,
        messages,
        **kwargs,
    ) -> ModelResponse:
        try:
            if self.model_name == "o1-preview":
                response = self.client.chat.completions.create(model=self.model_name, messages=messages[1:])
            else:
                response = self.client.chat.completions.create(model=self.model_name, messages=messages)
            return ModelResponse(
                {"role": "assistant", "content": response.choices[0].message.content or "None"},
                {
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            )
        except Exception as error:
            return ModelResponse(
                {"role": "assistant", "content": str(error)},
                {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
            )

    def embedding(self, text, model="text-embedding-ada-002") -> EmbeddingResponse:
        return EmbeddingResponse(np.array(self.client.embeddings.create(input=[text], model=model).data[0].embedding))

    def image(self, prompt: str) -> ImageResponse:
        self._initialize_image_client()
        try:
            if self.image_client:
                response = self.image_client.images.generate(
                    prompt=prompt, model=self.model_name, quality="hd", response_format="url", style="vivid"
                )
            else:
                raise ValueError("Image client initialization failed")

            return ImageResponse(response.data[0].url)
        except Exception as error:
            raise error
