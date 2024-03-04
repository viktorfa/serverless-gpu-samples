import torch
import torch.utils.benchmark as benchmark
from pipeline import Pipeline, Variable, entity, pipe


# Put your model inside of the below entity class
@entity
class MyModelClass:
    @pipe(run_once=True, on_startup=True)
    def load(self) -> None:
        # Perform any operations needed to load your model here
        print("Loading model...")

        ...

        print("Model loaded!")

    @pipe
    def predict(self, output_number: int) -> dict:
        print("Predicting...")

        dtype = torch.float32
        device = torch.device("cuda")  # Use "cpu" for CPU benchmarking
        sizes = [1024, 2048, 4096]  # Example sizes
        results = {}

        for size in sizes:
            # Define x and y inside the loop to ensure they're freshly allocated for each size
            x = torch.rand(size, size, device=device, dtype=dtype)
            y = torch.rand(size, size, device=device, dtype=dtype)
            timer = benchmark.Timer(
                stmt='torch.matmul(x, y)',
                globals={'x': x, 'y': y}  # Define globals directly here
            )
            time_mean = timer.timeit(100).mean
            print(f"Size: {size}x{size}, Time: {time_mean:.3f} seconds")
            results[size] = {"mean_time": time_mean}

            print("Prediction complete!")
        return results


with Pipeline() as builder:
    input_var = Variable(
        int,
        description="A basic input number to do things with",
        title="Input number",
    )

    my_model = MyModelClass()
    my_model.load()

    output_var = my_model.predict(input_var)

    builder.output(output_var)

my_new_pipeline = builder.get_pipeline()
