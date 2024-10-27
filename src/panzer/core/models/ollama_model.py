import time
import json
import requests
from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.responses.embedding_response import EmbeddingResponse
from core.models.base_model_client import BaseModelClient


class OllamaModel(BaseModel):
    def __init__(self, endpoint: str, model_name: str):
        self.model_name = model_name
        self.endpoint = endpoint

    def test_connection(self):
        pass

    def chat(
        self, messages, max_retries=10, initial_delay=1, backoff_factor=2, jitter=0.1, max_delay=64, **kwargs
    ) -> ModelResponse:
        """
        Sends a request to the model with exponential backoff retry policy.
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
                data = {
                    "model": self.model_name,
                    "stream": False,
                    "messages": messages[1:],  # does not have system role
                }

                headers = {
                    "Content-Type": "application/json",
                }

                response = requests.post(self.endpoint, headers=headers, data=json.dumps(data))

                if response.status_code == 200:
                    response_text = response.text
                    data = json.loads(response_text)
                    return ModelResponse(
                        data["message"], {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4}
                    )
                else:
                    error_message = f"Error: {response.status_code} - {response.text}"
                    return ModelResponse(
                        {"role": "assistant", "content": error_message},
                        {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
                    )

            except Exception as err:
                if retries == max_retries - 1:
                    break
                else:
                    # TODO: Clean up
                    # sleep_time = calculate_sleep_time(retries, initial_delay, backoff_factor, jitter, max_delay)
                    # print(log_retries(retries, sleep_time, err))
                    time.sleep(10)
                    retries += 1

        return ModelResponse(
            {"role": "assistant", "content": "Maximum number of retries exceeded."},
            {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
        )

    def image(self) -> ImageResponse:
        raise NotImplementedError()

    def embedding(self) -> EmbeddingResponse:
        raise NotImplementedError()

