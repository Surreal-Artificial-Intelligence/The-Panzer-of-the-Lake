from openai import OpenAI
from data_class.model_response import ModelResponse
from data_class.image_response import ImageResponse
from interfaces.base_model import BaseModel


class TogetherAIModel(BaseModel):
    def __init__(self, api_key: str, model_name: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
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

    def chat(self, messages) -> ModelResponse:
        """
        Sends a request to the model with exponential backoff retry policy.

        Parameters
        ----------
        message : str
            The message to send to the model.

        Returns
        -------
        response : ModelResponse
            The response from the model.
        """
        response = None
        try:
            response = self.client.chat.completions.create(model=self.model_name, messages=messages)
            return ModelResponse(
                {"role": "assistant", "content": response.choices[0].message.content or "None"},
                {
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            )
        except Exception as error:
            print(error)
            return ModelResponse(
                {"role": "assistant", "content": str(error)},
                {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            )

    def image(self, prompt: str):
        """Generate an image using the OpenAI library with Together AI"""
        response = self.client.images.generate(
            prompt=prompt,
            model=self.model_name,
            n=1,
        )
        return response
