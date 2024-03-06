import modal
import subprocess


stub = modal.Stub("hello-gpu")


@stub.function(gpu=modal.gpu.T4(count=1), container_idle_timeout=2)
def f(x: int) -> str:
    has_gpu = check_gpu()
    return f"Your number is {x}! has gpu: {has_gpu}"


@stub.local_entrypoint()
def main():
    # run the function locally
    print(f.local(1000))

    # run the function remotely on Modal
    print(f.remote(500))


def check_gpu():
    try:
        # Try running `nvidia-smi` to list NVIDIA GPUs
        subprocess.check_output(["nvidia-smi"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # `nvidia-smi` is not found or an error occurred
        return False
