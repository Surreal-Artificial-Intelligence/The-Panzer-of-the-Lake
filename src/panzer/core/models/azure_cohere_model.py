import requests
import logging
from core.models.base_model_client import BaseModelClient
from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.responses.embedding_response import EmbeddingResponse


class CohereAzureModel(BaseModelClient):
    """The CohereAzureModel class is a wrapper around the Cohere Azure API. It provides methods for sending messages to
    the Cohere Azure API and receiving responses from the API."""

    def __init__(self, api_key: str, api_version: str, azure_endpoint: str):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        if not self.api_key:
            raise ValueError("No API key provided")

    def models(self):
        raise NotImplementedError()

    def test_connection(self):
        """Test the connection to the remote resource"""
        data = {
            "messages": [{"role": "system", "content": "You are a helpful assistant."}],
            "temperature": 0.7,
            "top_p": 1,
            "stop": [],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            url = self.azure_endpoint
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_error:
            logging.error("HTTP error occurred: %s", http_error)
        except requests.exceptions.ConnectionError as conn_error:
            logging.error("Connection error occurred: %s", conn_error)
        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout error occurred: %s", timeout_error)
        except requests.exceptions.RequestException as request_error:
            logging.error("Error occurred while sending the request: %s", request_error)
        except Exception as error:
            raise error

    def chat(
        self,
        messages,
        model_name:str,
        **kwargs,
    ) -> ModelResponse:
        """Sends a request to the model with exponential backoff retry policy.
        Parameters
        ----------
        message : str
            The message to send to the model.
        kwargs : dict
            Additional keyword arguments to be passed to the ChatCompletion.create() function.

        Returns
        -------
        response : str
            The response from the model.
        """

        try:
            url = self.azure_endpoint
            response = requests.post(
                url,
                json={"messages": messages},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
            )
            response.raise_for_status()
            response = response.json()
            return ModelResponse(response["choices"][0]["message"], response["usage"])
        except Exception as error:
            return ModelResponse(
                {"role": "assistant", "content": str(error)},
                {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
            )

    def image(self) -> ImageResponse:
        raise NotImplementedError()

    def embedding(self) -> EmbeddingResponse:
        raise NotImplementedError()
