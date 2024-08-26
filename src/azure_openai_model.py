import time
import streamlit as st
from openai import AzureOpenAI
from utils import calculate_sleep_time


class AzureOpenAIModel:
    """Azure OpenAI Model class. This class is a wrapper around the Azure OpenAI API. It provides methods for sending
    messages to the model, and retrieving responses from it. It also provides methods for logging retries and sleeping
    before retrying. The class is initialized with an Azure OpenAI API key, version, endpoint, and model name.
    """

    def __init__(
        self, api_key: str, api_version: str, azure_endpoint: str, model_name: str
    ):
        self.azure_openai_client = AzureOpenAI(
            api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
        )
        self.model_name = model_name

    def test_connection(self):
        """Test the connection to the remote resource"""
        response = self.azure_openai_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are an AI assistant"},
                {"role": "user", "content": "Hello"},
            ],
        )
        return response

    def chat(
        self,
        messages,
        model=st.secrets["AZURE_OPENAI_DEPLOYMENT"],
        max_retries=10,
        initial_delay=1,
        backoff_factor=2,
        jitter=0.1,
        max_delay=64,
        on_retry=None,
        **kwargs,
    ) -> object:
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
                return self.azure_openai_client.chat.completions.create(
                    model=self.model_name, messages=messages
                )
            except Exception as error:
                if retries == max_retries - 1:
                    raise error  # Raise the exception if max_retries reached
                else:
                    sleep_time = calculate_sleep_time(
                        retries, initial_delay, backoff_factor, jitter, max_delay
                    )
                    if on_retry is not None:
                        on_retry(retries, sleep_time, error)
                    time.sleep(sleep_time)  
                    retries += 1

    def chat_raw(self,
        messages,
        model=st.secrets["AZURE_OPENAI_DEPLOYMENT"],
        max_retries=10,
        initial_delay=1,
        backoff_factor=2,
        jitter=0.1,
        max_delay=64,
        on_retry=None,
        **kwargs,) -> object:
        """Sends a request to the model with exponential backoff retry policy using raw HTTP request.

        Parameters
        ----------
        message : str
            The message to send to the model.

        Returns
        -------
        response : str
            The response from the model.
        """
        raise NotImplementedError("This method is not implemented")

    # def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    #     return client.embeddings.create(input = [text], model=model).data[0].embedding
