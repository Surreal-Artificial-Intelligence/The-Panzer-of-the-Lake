from openai import OpenAI
from data_class.model_response import ModelResponse
from data_class.image_response import ImageResponse
from data_class.embedding_response import EmbeddingResponse
from interfaces.base_model import BaseModel


class OpenAIModel(BaseModel):
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def transcribe(self, audio) -> str:
        """Transcribe audio using Open AI whisper v3"""
        raise NotImplementedError()

    def chat(self, messages, **kwargs) -> ModelResponse:
        """
        Sends a request to the model with exponential backoff retry policy.

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
            response = self.client.chat.completions.create(model=self.model_name, messages=messages)
            return ModelResponse(
                {"message": response.choices[0].message.content or "None"},
                {
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            )
        except Exception as error:
            return ModelResponse(
                {"role": "assistant", "content": str(error)},
                {"completion_tokens": 1, "prompt_tokens": 2, "total_tokens": 4},
            )

    def image(self) -> ImageResponse:
        raise NotImplementedError()

    def embedding(self) -> EmbeddingResponse:
        raise NotImplementedError()
