import time
import requests
import logging

from interfaces.base_model import BaseModel
from data_class.model_response import ModelResponse
from utils import calculate_sleep_time


class GenericHttpsModel(BaseModel):
    """A universal wrapper class to chat to any LLM via HTTPS POST calls."""

    def __init__(self, api_key: str, api_version: str, endpoint: str, model_name: str):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("No API key provided")
        self.endpoint = endpoint
        self.api_version = api_version
        self.model_name = model_name

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
            url = self.endpoint
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
        max_retries=10,
        initial_delay=1,
        backoff_factor=2,
        jitter=0.1,
        max_delay=64,
        on_retry=None,
        **kwargs,
    ) -> ModelResponse:
        """Sends a request to the model with exponential backoff retry policy.
        Parameters
        ----------
        message : str
            The message to send to the model.
        max_retries : int, optional
            The maximum number of retries before giving up. Default is 10.
        initial_delay : float, optional
            The initial delay in seconds between retries. Default is 1.
        backoff_factor : float, optional
            The factor by which the delay increases exponentially. Default is 2.
        jitter : float, optional
            The random factor to apply to the sleep time calculation. Default is 0.1.
        max_delay : float, optional
            The maximum delay in seconds between retries. Default is 64.
        on_retry : callable, optional
            An optional callback function that is executed on each retry. Default is None.
        kwargs : dict
            Additional keyword arguments to be passed to the ChatCompletion.create() function.

        Returns
        -------
        response : str
            The response from the model.
        """

        payload = {
            "model": self.model_name,
            "temperature": 0.2,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "messages": messages,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                response = response.json()
                return ModelResponse(response["choices"][0]["message"], response["usage"])
            except Exception as error:
                if retries == max_retries - 1:
                    raise error
                else:
                    sleep_time = calculate_sleep_time(retries, initial_delay, backoff_factor, jitter, max_delay)
                    if on_retry is not None:
                        on_retry(retries, sleep_time, error)
                    time.sleep(sleep_time)
                    retries += 1

        return ModelResponse(
            {"role": "assistant", "content": "Maximum number of retries exceeded."},
            {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
        )

    def image(self, model_name: str):
        payload = {
            "prompt": "cat floating in space, cinematic",
            "model": model_name,
            "steps": 20,
            "n": 1,
            "height": 1024,
            "width": 1024,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            response = response.json()
            return response
        except Exception as error:
            print(error)


    # def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    #     return client.embeddings.create(input = [text], model=model).data[0].embedding
