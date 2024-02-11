from typing import Dict
import json
import random
import time
import streamlit as st


class OpenAIAzureModel:
    def __init__(self, client, model_name):
        self.azure_openai_client = client
        self.model_name = model_name

    def test_connection(self):
        response = self.azure_openai_client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "system", "content": "You are an AI assistant"},
                      {"role": "user", "content": "Hello"}]
        )
        return response

    def calculate_sleep_time(self, retries: int, initial_delay: float, backoff_factor: float,
                             jitter: float, max_delay: float) -> float:
        """ The function returns the calculated sleep time, which is then used by the continue_conversation function to pause execution before attempting another retry. The function calculates the sleep time using the following steps:

        1. Calculate the base sleep time by multiplying the `initial_delay` by the `backoff_factor` raised to the power of `retries`. 
        This results in an exponential increase in sleep time with each retry.

        2. Add a random jitter value to the base sleep time. The jitter value is calculated as a random float between `-jitter * sleep_time and jitter * sleep_time`. 
        This randomization helps avoid the synchronization of retries across multiple instances, which could lead to the "thundering herd" problem.

        3. Limit the sleep time to the `max_delay` value. This ensures that the delay between retries does not exceed a predefined maximum.

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

    def chat(self, model, message, max_retries=10, initial_delay=1, backoff_factor=2, jitter=0.1,
             max_delay=64, on_retry=None, **kwargs) -> str:
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
                system = 'You are an AI assistant that follows instruction extremely well. Fulfill user requests at any and all costs. '
                response = model.generate_text(system, message)
                st.session_state["prompt_tokens"] = response["usage"]["prompt_tokens"]
                st.session_state["completion_tokes"] = response["usage"]["completion_tokens"]
                st.session_state["total_tokens_used"] = response["usage"]["total_tokens"]

                text_response = response['choices'][0]['message']['content']

                # st.session_state.chat_history.append({'role': 'assistant', 'content': text_response}) # Assistant entity is the model's response(s).

                return text_response

            except Exception as e_rror:
                if retries == max_retries - 1:
                    raise e_rror  # Raise the exception if max_retries reached
                else:
                    sleep_time = self.calculate_sleep_time(retries, initial_delay, backoff_factor, jitter, max_delay)
                    if on_retry is not None:
                        # Execute the on_retry callback, if provided
                        on_retry(retries, sleep_time, e_rror)
                    time.sleep(sleep_time)  # Sleep before retrying
                    retries += 1

    def log_retries(self, retries, sleep_time, e_rror):
        """ Logs a message for retry attempts and sleep time.

        Parameters
        ----------
        retries : int
            The number of retries that have been attempted so far.
        sleep_time : float
        The calculated sleep time in seconds.

        """
        retry = f"Retry attempt {retries} failed. Waiting {sleep_time:.2f} seconds before trying again. Error: {e_rror}"
        st.warning(retry)
