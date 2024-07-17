import random
import time
import streamlit as st
from openai import AzureOpenAI


class AzureOpenAIModel:
    """Azure OpenAI Model class. This class is a wrapper around the Azure OpenAI API. It provides methods for sending
    messages to the model, and retrieving responses from it. It also provides methods for logging retries and sleeping
    before retrying. The class is initialized with an Azure OpenAI API key, version, endpoint, and model name.
    """

    def __init__(self, api_key: str, api_version: str, azure_endpoint: str, model_name: str):
        self.azure_openai_client = AzureOpenAI(api_key=api_key,
                                               api_version=api_version,
                                               azure_endpoint=azure_endpoint)
        self.model_name = model_name

    def test_connection(self):
        """Test the connection to the remote resource"""
        response = self.azure_openai_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": "You are an AI assistant"},
                      {"role": "user", "content": "Hello"}]
        )
        return response

    def calculate_sleep_time(self, retries: int, initial_delay: float, backoff_factor: float,
                             jitter: float, max_delay: float) -> float:
        """ The function returns the calculated sleep time, which is then used by the continue_conversation function to
        pause execution before attempting another retry. The function calculates the sleep time using the following
        steps:

        1. Calculate the base sleep time by multiplying the `initial_delay` by the `backoff_factor` raised to the power
           of `retries`.
        This results in an exponential increase in sleep time with each retry.

        2. Add a random jitter value to the base sleep time. The jitter value is calculated as a random float between
           `-jitter * sleep_time and jitter * sleep_time`.
        This randomization helps avoid the synchronization of retries across multiple instances, which could lead to the
        "thundering herd" problem.

        3. Limit the sleep time to the `max_delay` value. This ensures that the delay between retries does not exceed a
           predefined maximum.

        Calculates the sleep time for a retry attempt using exponential backoff with jitter.

        Parameters
        ----------
        retries : int
            The number of retries that have been attempted so far.
        initial_delay : float
            The initial delay in seconds between retries.
        backoff_factor : float
            The factor by which the delay increases exponentially.
        jitter : float
            The random factor to apply to the sleep time calculation.
        max_delay : float
            The maximum delay in seconds between retries.

        Returns
        -------
        sleep_time : float
            The calculated sleep time in seconds.
        """
        sleep_time = initial_delay * (backoff_factor ** retries)
        sleep_time += random.uniform(-jitter * sleep_time, jitter * sleep_time)
        return min(sleep_time, max_delay)

    def chat(self, messages, model=st.secrets['AZURE_OPENAI_DEPLOYMENT'],
             max_retries=10, initial_delay=1, backoff_factor=2, jitter=0.1,
             max_delay=64, on_retry=None, **kwargs) -> object:
        """ Sends a request to the model with exponential backoff retry policy.
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
                    model=self.model_name,
                    messages=messages
                )
            except Exception as error:
                if retries == max_retries - 1:
                    raise error  # Raise the exception if max_retries reached
                else:
                    sleep_time = self.calculate_sleep_time(retries, initial_delay, backoff_factor, jitter, max_delay)
                    if on_retry is not None:
                        # Execute the on_retry callback, if provided
                        on_retry(retries, sleep_time, error)
                    time.sleep(sleep_time)  # Sleep before retrying
                    retries += 1

    def log_retries(self, retries, sleep_time, error):
        """ Logs a message for retry attempts and sleep time.

        Parameters
        ----------
        retries : int
            The number of retries that have been attempted so far.
        sleep_time : float
        The calculated sleep time in seconds.

        """
        retry = f"Retry attempt {retries} failed. Waiting {sleep_time:.2f} seconds before trying again. Error: {error}"
        st.warning(retry)

    # def generate_embeddings(text, model="text-embedding-ada-002"): # model = "deployment_name"
    #     return client.embeddings.create(input = [text], model=model).data[0].embedding
