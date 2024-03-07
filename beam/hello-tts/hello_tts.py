import time
import os
from typing import Any, TypedDict
import torch
from transformers import BarkModel, AutoProcessor
from scipy.io import wavfile


from beam import App, Runtime, Image, Output, GpuType, Volume


app = App(
    "hello-tts",
    runtime=Runtime(
        cpu=7,
        memory="30Gi",
        gpu=GpuType.A10G,
        image=Image(
            python_version="python3.10",
            python_packages=[
                "torch",
                "numpy",
                "transformers",
                "optimum",
                "accelerate",
                "pydantic==2.6.3",
                "scipy",
            ],
        ),
    ),
    volumes=[Volume(name="cached_models", path="./cached_models")],
)


os.environ["HF_HUB_CACHE"] = "./cached_models"


class HelloTtsParams(TypedDict):
    invoke_time_s: float


class HelloTtsResult(TypedDict):
    infer_time_s: float
    load_time_s: float
    time_to_infer_s: float
    tts_string: str
    is_cold_start: bool
    cold_start_time_s: float


# Triggers determine how your app is deployed
@app.rest_api(outputs=[Output(path="generated_audio.wav")])
def run(**kwargs: HelloTtsParams) -> HelloTtsResult:
    print("Inferring")
    print("kwargs", kwargs)
    invoke_time_s = float(kwargs["invoke_time_s"])

    start_load = time.time()
    cold_start_time_s = start_load - invoke_time_s
    is_cold_start = cold_start_time_s > 2

    print("Running on container startup")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts_model = BarkModel.from_pretrained(
        "suno/bark",
        # torch_dtype=torch.float16,  # Half precision
        # attn_implementation="flash_attention_2",  # There's a bug with Flash Attention and Bark https://discuss.huggingface.co/t/barkmodel-not-intialising-with-flash-attention-2/75432
        # local_files_only=True,
        cache_dir="./cached_models",
    ).to(device)
    tts_model = tts_model.to_bettertransformer()
    tts_processor = AutoProcessor.from_pretrained(
        "suno/bark",
        # local_files_only=True,
        cache_dir="./cached_models",
    )
    end_load = time.time()
    load_time = end_load - start_load

    start_infer = time.time()
    time_to_infer = start_infer - invoke_time_s

    tts_string = f"I used {load_time:.2f} seconds to load the model and {time_to_infer:.2f} seconds to get here"
    tts_inputs = tts_processor(tts_string, return_tensors="pt")
    tts_inputs = {key: value.to(device) for key, value in tts_inputs.items()}
    tts_result = tts_model.generate(**tts_inputs)
    audio_array = tts_result.cpu().numpy().squeeze()
    sample_rate = tts_model.generation_config.sample_rate

    wavfile.write("generated_audio.wav", sample_rate, audio_array)

    end_infer = time.time()
    infer_time = end_infer - start_infer

    result = HelloTtsResult(
        infer_time_s=infer_time,
        load_time_s=load_time,
        time_to_infer_s=time_to_infer,
        tts_string=tts_string,
        is_cold_start=is_cold_start,
        cold_start_time_s=cold_start_time_s,
    )

    return result
