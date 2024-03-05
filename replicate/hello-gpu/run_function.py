import time
import os
import replicate

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]  # Needs to be in environment


def run_function():
    start_time = time.perf_counter()
    result = replicate.run(
        "viktorfa/hello-gpu:7ba7d6ce64dcaf85b0c1efb6e1168417c6c05b0b76a9217394e2a153be662dec",
        input={"number": 5},
    )
    print(result)
    end_time = time.perf_counter()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    return result


if __name__ == "__main__":
    run_function()
