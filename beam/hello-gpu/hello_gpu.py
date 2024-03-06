import subprocess
from beam import App, Runtime

app = App(name="hello-gpu", runtime=Runtime(gpu="T4"))


@app.run()
def run(**kwargs):
    print("🔮 This is running remotely on Beam!")
    print(f"🔮 Inputs: {kwargs}")

    has_gpu = check_gpu()
    print(f"🔮 has_gpu: {has_gpu}")

    number = kwargs.get("x", 0)
    return f"Your number is {number}! 🎉, has_gpu: {has_gpu}"


@app.rest_api()
def api(x: int):
    print("🔮 This is running remotely on Beam!")
    print(f"🔮 x: {x}")

    has_gpu = check_gpu()
    print(f"🔮 has_gpu: {has_gpu}")

    number = x
    return f"Your number is {number}! 🎉, has_gpu: {has_gpu}"


def check_gpu():
    try:
        # Try running `nvidia-smi` to list NVIDIA GPUs
        subprocess.check_output(["nvidia-smi"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # `nvidia-smi` is not found or an error occurred
        return False
