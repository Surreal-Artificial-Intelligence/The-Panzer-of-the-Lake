import numpy as np
from openai import AzureOpenAI
from core.models.base_model_client import BaseModelClient
from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.responses.embedding_response import EmbeddingResponse
from typing import Optional


class AzureOpenAIModel(BaseModelClient):
    """Azure OpenAI Model class. This class is a wrapper around the Azure OpenAI API. It provides methods for sending
    messages to the model, and retrieving responses from it. It also provides methods for logging retries and sleeping
    before retrying. The class is initialized with an Azure OpenAI API key, version, endpoint, and model name.
    """

    def __init__(
        self,
        api_key: str,
        api_version: str,
        azure_endpoint: str,
        image_endpoint: Optional[str] = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.api_version = api_version
        self.azure_endpoint = azure_endpoint

        self.default_headers = kwargs.get("default_headers", {})

        self.image_endpoint = image_endpoint
        self.image_client = None

    def _initialize_image_client(self):
        if not self.image_endpoint:
            raise ValueError("Azure OpenAI image endpoint is required")
        self.image_client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.image_endpoint,
            default_headers=self.default_headers,
        )

    def models(self):
        raise NotImplementedError()

    def chat(
        self,
        messages,
        model_name: str,
        **kwargs,
    ) -> ModelResponse:
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint.format(model_name),
            **kwargs,
        )

        if model_name == "o1-preview":
            response = client.chat.completions.create(model=model_name, messages=messages[1:])
        else:
            response = client.chat.completions.create(model=model_name, messages=messages)
        return ModelResponse(
            {"role": "assistant", "content": response.choices[0].message.content or "None"},
            {
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
        )

    def embedding(
        self,
        text,
        model="text-embedding-ada-002",
        **kwargs,
    ) -> EmbeddingResponse:
        client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint.format(model),
            **kwargs,
        )  # TODO: Test that it works (RAG implementation)
        return EmbeddingResponse(np.array(client.embeddings.create(input=[text], model=model).data[0].embedding))

    def image(self, model_name: str, prompt: str) -> ImageResponse:
        self._initialize_image_client()
        if self.image_client:
            response = self.image_client.images.generate(
                prompt=prompt, model=model_name, quality="hd", response_format="url", style="vivid"
            )
        else:
            raise ValueError("Image client initialization failed")

        return ImageResponse(response.data[0].url)
