from typing import Dict
import json
import random
import time
from model_utils import calculate_sleep_time, log_retries
from interfaces.tts_model import TTSModel


class XTTSV2Model(TTSModel):
    def __init__(self):
        pass

    def test_connection(self):
        pass

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
