import modal
import torch
import torch.utils.benchmark as benchmark

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("torch")
    .pip_install("numpy")
    .env({"HALT_AND_CATCH_FIRE": 0})
)

stub = modal.Stub("hello-torch")


@stub.cls(gpu=modal.gpu.T4(count=1), container_idle_timeout=2, image=image)
class Model:
    @modal.enter()
    def run_this_on_container_startup(self):
        print("Running on container startup")

    @modal.method()
    def predict(self, x: int) -> dict:
        dtype = torch.float32
        device = torch.device("cuda")  # Use "cpu" for CPU benchmarking
        sizes = [1024, 2048, 4096]  # Example sizes
        results = {}

        for size in sizes:
            # Define x and y inside the loop to ensure they're freshly allocated for each size
            x = torch.rand(size, size, device=device, dtype=dtype)
            y = torch.rand(size, size, device=device, dtype=dtype)
            timer = benchmark.Timer(
                stmt="torch.matmul(x, y)",
                globals={"x": x, "y": y},  # Define globals directly here
            )
            time_mean = timer.timeit(100).mean
            print(f"Size: {size}x{size}, Time: {time_mean:.3f} seconds")
            results[size] = {"mean_time": time_mean}

            print("Prediction complete!")
        return results


@stub.local_entrypoint()
def main():
    result = Model().predict.remote(5)

    print("result", result)
