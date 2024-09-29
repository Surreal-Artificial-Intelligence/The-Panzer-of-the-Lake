import time
from openai import OpenAI
from data_class.model_response import ModelResponse
from utils import calculate_sleep_time, log_retries
from interfaces.base_model import BaseModel


class OpenAIModel(BaseModel):
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def test_connection(self):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": "You are an AI assistant"}, {"role": "user", "content": "Hello"}],
        )
        return response

    def transcribe(self, audio) -> str:
        """Transcribe audio using Open AI whisper v3"""
        raise NotImplementedError()

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
                response = self.client.chat.completions.create(model=self.model_name, messages=messages)
                return ModelResponse(
                    {"message": response.choices[0].message.content or "None"},
                    {
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                )
            except Exception as e_rror:
                if retries == max_retries - 1:
                    raise e_rror  # Raise the exception if max_retries reached
                else:
                    sleep_time = calculate_sleep_time(retries, initial_delay, backoff_factor, jitter, max_delay)
                    if log_retries is not None:
                        # Execute the on_retry callback, if provided
                        print(log_retries(retries, sleep_time, e_rror))
                    time.sleep(sleep_time)  # Sleep before retrying
                    retries += 1

        return ModelResponse(
            {"role": "assistant", "content": "Maximum number of retries exceeded."},
            {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
        )
