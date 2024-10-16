from typing import Dict
import time
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


          # api_url = "http://localhost:8000/text-to-speech"
    # try:
    #     # Sending a POST request
    #     data = {"text": text, "lang": lang}

    #     tts_response = requests.post(api_url, headers="headers", json=data)

    #     if tts_response.status_code == 200:
    #         # Decode the binary data to a string
    #         json_string = tts_response.content.decode("utf-8")
    #         # Convert the JSON string to a Python list
    #         audio_list = json.loads(json_string)
    #         audio_array = np.array(audio_list)
    #         return audio_array
    #     else:
    #         print(f"Error: {tts_response.status_code} - {tts_response.text}")
    # except Exception as e:
    #     # Print an error message in case of an exception
    #     print(f"Exception: {str(e)}")
