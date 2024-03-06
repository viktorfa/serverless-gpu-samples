import torch
import torch.utils.benchmark as benchmark
import json


class InferlessPythonModel:
    def initialize(self):
        print("Initializing")

    def infer(self, inputs: dict):
        print("Inferring")
        number = int(inputs["x"])

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
        return {"results": json.dumps(results)}

    def finalize(self):
        print("Finalizing")
