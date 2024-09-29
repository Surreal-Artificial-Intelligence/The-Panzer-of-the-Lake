import pathlib
from data_class.model_response import ModelResponse
from interfaces.base_model import BaseModel


class TransformersModel:
    def __init__(self, model_name_or_path: str) -> None:
        self.model_name_or_path = model_name_or_path

    def test_connection(self) -> str:
        pass

    def chat(self) -> ModelResponse:
        pass

    def transcribe(self, audio, model_path) -> str:
        """Transcribe audio using Open AI whisper v3 and the transformers library"""

        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-large-v3"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )

        model_path = pathlib.Path(model_path)

        model.to(device)
        processor = AutoProcessor.from_pretrained(model_path)

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

        result = pipe(audio)

        return str(result)
