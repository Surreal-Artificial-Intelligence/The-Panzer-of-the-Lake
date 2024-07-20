import time
import requests
import logging
from interfaces.IModel import IModel
from utils import calculate_sleep_time


class CohereAzureModel(IModel):
    """The CohereAzureModel class is a wrapper around the Cohere Azure API. It provides methods for sending messages to
    the Cohere Azure API and receiving responses from the API."""

    def __init__(
        self, api_key: str, api_version: str, azure_endpoint: str, model_name: str
    ):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.api_version = api_version
        if not self.api_key:
            raise ValueError("No API key provided")

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
        max_retries=10,
        initial_delay=1,
        backoff_factor=2,
        jitter=0.1,
        max_delay=64,
        on_retry=None,
        **kwargs,
    ) -> str:
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

        retries = 0
        while retries < max_retries:
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
                return response.json()
            except Exception as error:
                if retries == max_retries - 1:
                    raise error
                else:
                    sleep_time = calculate_sleep_time(
                        retries, initial_delay, backoff_factor, jitter, max_delay
                    )
                    if on_retry is not None:
                        on_retry(retries, sleep_time, error)
                    time.sleep(sleep_time)
                    retries += 1

        return "Maximum number of retries exceeded."

    # def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    #     return client.embeddings.create(input = [text], model=model).data[0].embedding
