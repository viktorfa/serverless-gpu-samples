import os
import modal
import asyncio
import libsql_client
import time
from functools import partial
import requests
from dotenv import load_dotenv


image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("libsql-client")
    .pip_install("asyncio")
    .pip_install("requests")
    .pip_install("python-dotenv")
    .env({"HALT_AND_CATCH_FIRE": 0})
)

stub = modal.Stub("run-benchmark")


print("is_local() module", modal.is_local())


@stub.function(
    image=image,
    secrets=[
        modal.Secret.from_dict({"DB_URL": "libsql://gpu-benchmark-viktorfa.turso.io"}),
        modal.Secret.from_name("benchmark-secrets"),
    ],
    schedule=modal.Period(hours=6),
)
async def my_function():
    print("is_local() function", modal.is_local())
    print('os.getenv("DB_URL")', os.getenv("DB_URL"))
    hello_gpu_f = modal.Function.lookup("hello-gpu", "f")
    hello_gpu = partial(hello_gpu_f.remote, x=15)
    hello_torch_cls = modal.Cls.lookup("hello-torch", "Model")
    hello_torch_obj = hello_torch_cls()
    hello_torch = partial(hello_torch_obj.predict.remote, x=12)

    hello_gpu_inferless = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://m-8998c4c09b5c4483ac5612770fc01b6e-m.default.model-v1.inferless.com/v2/models/hello-gpu_8998c4c09b5c4483ac5612770fc01b6e/versions/1/infer",
            headers={
                "Authorization": f"Bearer {os.environ['INFERLESS_API_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": [
                    {"name": "x", "shape": [1], "data": ["4"], "datatype": "BYTES"}
                ],
            },
        ),
    )
    hello_torch_inferless = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://m-230039ace7cf4d648cd250b16e4a3f59-m.default.model-v1.inferless.com/v2/models/hello-torch_230039ace7cf4d648cd250b16e4a3f59/versions/1/infer",
            headers={
                "Authorization": f"Bearer {os.environ['INFERLESS_API_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": [
                    {"name": "x", "shape": [1], "data": ["4"], "datatype": "BYTES"}
                ],
            },
        ),
    )

    hello_gpu_runpod = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://api.runpod.ai/v2/vk41rg62gap3gs/runsync",
            headers={
                "Authorization": f"Bearer {os.environ['RUNPOD_API_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "input": {"x": 4},
            },
        ),
    )
    hello_torch_runpod = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://api.runpod.ai/v2/spuu8pqxc80gnm/runsync",
            headers={
                "Authorization": f"Bearer {os.environ['RUNPOD_API_TOKEN']}",
                "Content-Type": "application/json",
            },
            json={
                "input": {"x": 8},
            },
        ),
    )

    hello_gpu_beam = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://u8g9t.apps.beam.cloud",
            headers={
                "Content-Type": "application/json",
            },
            json={"x": 4},
            auth=(os.environ["BEAM_API_CLIENT"], os.environ["BEAM_API_SECRET"]),
        ),
    )
    hello_torch_beam = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://motbx.apps.beam.cloud",
            headers={
                "Content-Type": "application/json",
            },
            json={"x": 8},
            auth=(os.environ["BEAM_API_CLIENT"], os.environ["BEAM_API_SECRET"]),
        ),
    )

    configs = [
        {
            "vendor": "modal",
            "gpu_type": "t4",
            "function_type": "hello_gpu",
            "function": hello_gpu,
        },
        {
            "vendor": "modal",
            "gpu_type": "t4",
            "function_type": "hello_torch",
            "function": hello_torch,
        },
        {
            "vendor": "inferless",
            "gpu_type": "t4",
            "function_type": "hello_gpu",
            "function": hello_gpu_inferless,
        },
        {
            "vendor": "inferless",
            "gpu_type": "t4",
            "function_type": "hello_torch",
            "function": hello_torch_inferless,
        },
        {
            "vendor": "runpod",
            "gpu_type": "16gb",
            "function_type": "hello_gpu",
            "function": hello_gpu_runpod,
        },
        {
            "vendor": "runpod",
            "gpu_type": "16gb",
            "function_type": "hello_torch",
            "function": hello_torch_runpod,
        },
        {
            "vendor": "beam",
            "gpu_type": "t4",
            "function_type": "hello_gpu",
            "function": hello_gpu_beam,
        },
        {
            "vendor": "beam",
            "gpu_type": "t4",
            "function_type": "hello_torch",
            "function": hello_torch_beam,
        },
    ]

    async with libsql_client.create_client(
        url=os.getenv("DB_URL") or "libsql://gpu-benchmark-viktorfa.turso.io",
        auth_token=os.getenv("TURSO_DATABASE_AUTH_TOKEN"),
    ) as client:
        db_client = client

        # vendors = await db_client.execute("SELECT DISTINCT * FROM vendors")
        # print("vendors", vendors.rows)

        results = await asyncio.gather(
            *[run_and_record_result(db_client, config) for config in configs]
        )

        print(results)

    return "OK"


@stub.local_entrypoint()
def main():
    print("is_local() entrypoint", modal.is_local())
    load_dotenv(".env.local")

    result = asyncio.run(my_function.local())
    # result = my_function.remote()

    print("result", result)


def run_web_function(request_f: callable):
    result = request_f()

    print("result")
    print(result)

    return result.json()


def run_benchmark_wrapper(f: callable):
    start_time = time.perf_counter()
    is_success = False
    error = None
    result = None
    try:
        result = f()
        is_success = True
    except Exception as e:
        print(e)
        error = str(e)
    end_time = time.perf_counter()
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    return {
        "result": result,
        "total_time_s": end_time - start_time,
        "is_success": is_success,
        "error": error,
    }


async def run_and_record_result(db_client: libsql_client.Client, config: dict):
    # Run the benchmark wrapper to get the function execution time and success status
    benchmark_result = run_benchmark_wrapper(config["function"])

    # Insert the benchmark results into the database
    # Adapt the INSERT statement to match your database schema
    await db_client.execute(
        "INSERT INTO function_runs (vendor, total_time_ms, run_time_ms, gpu_type, function_type, status, error) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            config["vendor"],
            round(benchmark_result["total_time_s"] * 1000),
            round(benchmark_result["run_time_s"] * 1000)
            if benchmark_result.get("run_time_s")
            else None,
            config["gpu_type"],
            config["function_type"],
            "SUCCESS" if benchmark_result["is_success"] else "FAILURE",
            benchmark_result["error"] if benchmark_result.get("error") else None,
        ],
    )

    return benchmark_result
