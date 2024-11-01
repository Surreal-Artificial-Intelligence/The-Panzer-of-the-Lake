from core.models.responses.model_response import ModelResponse
from core.models.responses.image_response import ImageResponse
from core.models.responses.embedding_response import EmbeddingResponse
from core.models.base_model_client import BaseModelClient
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class TransformersModel(BaseModelClient):
    def __init__(self) -> None:
        pass

    def chat(
        self,
        model_name: str,
    ) -> ModelResponse:
        raise NotImplementedError()

    def models(self):
        raise NotImplementedError()

    def load_model(self, model_id) -> None:
        # TODO add support for using cache, downloaed model, or specify local model path
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )

        # model_path = pathlib.Path(model_path)

        model.to(device)
        processor = AutoProcessor.from_pretrained(model_id)

        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            chunk_length_s=30,
            batch_size=16,
            return_timestamps=True,
            torch_dtype=torch_dtype,
            device=device,
        )
        self.pipe = pipe

    def transcribe(self, audio, model_path) -> dict:
        """Transcribe audio using Open AI whisper v3 and the transformers library"""

        if not self.pipe:
            self.load_model(model_id="openai/whisper-large-v3")

        result = self.pipe(audio)

        return result  # type: ignore

    def image(
        self,
        model_name: str,
    ) -> ImageResponse:
        raise NotImplementedError()

    def embedding(
        self,
        model_name: str,
    ) -> EmbeddingResponse:
        raise NotImplementedError()
