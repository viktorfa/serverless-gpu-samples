import time
import os
import replicate

REPLICATE_API_TOKEN = os.environ["REPLICATE_API_TOKEN"]  # Needs to be in environment


def run_function():
    start_time = time.perf_counter()
    result = replicate.run(
        "viktorfa/hello-torch:3b297a2624682c11dfcbfd0aaecf9eebf14f2e8164069722cc733291ad5f22a0",
        input={"number": 5},
    )
    print(result)
    end_time = time.perf_counter()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

    return result


if __name__ == "__main__":
    run_function()
