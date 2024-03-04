import time
from pipeline.cloud.pipelines import run_pipeline



pointer = "vikfand/hello-torch:v5"
def run_function():
    start_time = time.perf_counter()
    result = run_pipeline(pointer, 1, wait_for_resources=True)
    end_time = time.perf_counter()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    print("result.state", result.state)
    print("result.error", result.error)
    print("result.outputs_formatted()", result.outputs_formatted())

    return result.outputs_formatted()



if __name__ == "__main__":
    run_function()