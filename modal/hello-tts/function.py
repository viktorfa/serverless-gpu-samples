import time
from typing import TypedDict
from pydantic import BaseModel
import modal
import torch
from transformers import BarkModel, AutoProcessor
from scipy.io import wavfile
from pathlib import Path
import tempfile
import base64
from huggingface_hub import snapshot_download

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("torch")
    .pip_install("numpy")
    .pip_install("transformers")
    .pip_install("optimum")
    .pip_install("accelerate")
    .pip_install("pydantic==2.6.3")
    .pip_install("scipy")
    .env({"HALT_AND_CATCH_FIRE": "0"})
)

stub = modal.Stub("hello-tts")


class HelloTtsParams(BaseModel):
    invoke_time_s: float


class HelloTtsResult(TypedDict):
    infer_time_s: float
    load_time_s: float
    time_to_infer_s: float
    tts_string: str
    result_url: str
    result_base64: str
    is_cold_start: bool
    cold_start_time_s: float


@stub.cls(
    container_idle_timeout=2,
    image=image,
    gpu=modal.gpu.A10G(count=1),
    cpu=7.0,
    memory=30 * 1024,
)
class HelloTts:
    @modal.build()
    def build_image(self):
        print("Building")
        snapshot_download("suno/bark")
        # BarkModel.from_pretrained("suno/bark")
        # AutoProcessor.from_pretrained("suno/bark")

    @modal.enter()
    def run_this_on_container_startup(self):
        self.start_load = time.time()
        self.is_cold_start = True
        print("Running on container startup")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts_model = BarkModel.from_pretrained(
            "suno/bark",
            # torch_dtype=torch.float16,  # Half precision
            # attn_implementation="flash_attention_2",  # There's a bug with Flash Attention and Bark https://discuss.huggingface.co/t/barkmodel-not-intialising-with-flash-attention-2/75432
            local_files_only=True,
        ).to(self.device)
        self.tts_model = self.tts_model.to_bettertransformer()
        self.tts_processor = AutoProcessor.from_pretrained(
            "suno/bark",
            local_files_only=True,
        )
        self.end_load = time.time()
        self.load_time = self.end_load - self.start_load

    @modal.method()
    def predict(self, invoke_time_s: float) -> HelloTtsResult:
        start_infer = time.time()
        time_to_infer = start_infer - invoke_time_s
        is_cold_start = invoke_time_s < self.start_load
        cold_start_time = self.start_load - invoke_time_s

        tts_string = f"I used {self.load_time:.2f} seconds to load the model and {time_to_infer:.2f} seconds to get here"
        tts_inputs = self.tts_processor(tts_string, return_tensors="pt")
        tts_inputs = {key: value.to(self.device) for key, value in tts_inputs.items()}
        tts_result = self.tts_model.generate(**tts_inputs)
        audio_array = tts_result.cpu().numpy().squeeze()
        sample_rate = self.tts_model.generation_config.sample_rate
        result_dir = Path(tempfile.mkdtemp())
        result_file_path = result_dir / "bark_generation.wav"
        wavfile.write(result_file_path, sample_rate, audio_array)

        end_infer = time.time()
        infer_time = end_infer - start_infer

        return HelloTtsResult(
            infer_time_s=infer_time,
            load_time_s=self.load_time,
            time_to_infer_s=time_to_infer,
            tts_string=tts_string,
            result_url=str(result_file_path),
            result_base64=encode_audio_to_base64(result_file_path),
            is_cold_start=is_cold_start,
            cold_start_time_s=cold_start_time,
        )


@stub.local_entrypoint()
def main():
    result = HelloTts().predict.remote(HelloTtsParams(invoke_time_s=time.time()))

    print("infer_time_s", result["infer_time_s"])
    print("load_time_s", result["load_time_s"])
    print("time_to_infer_s", result["time_to_infer_s"])
    print("tts_string", result["tts_string"])
    print("result_url", result["result_url"])
    print("is_cold_start", result["is_cold_start"])
    print("cold_start_time_s", result["cold_start_time_s"])

    print("result type", type(result))

    save_base64_audio_to_file(result["result_base64"], "result.wav")


def encode_audio_to_base64(result_file_path):
    with open(result_file_path, "rb") as audio_file:
        encoded_audio = base64.b64encode(audio_file.read()).decode("utf-8")
    return encoded_audio


def save_base64_audio_to_file(encoded_audio, output_file_path):
    audio_data = base64.b64decode(encoded_audio)
    with open(output_file_path, "wb") as file:
        file.write(audio_data)
