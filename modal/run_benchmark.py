import os
import modal
import asyncio
import libsql_client
import time
from functools import partial
import requests
from dotenv import load_dotenv
import replicate
from pydantic import BaseModel


image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("libsql-client")
    .pip_install("asyncio")
    .pip_install("requests")
    .pip_install("python-dotenv")
    .pip_install("replicate")
    .pip_install("pydantic")
    .env({"HALT_AND_CATCH_FIRE": 0})
)

stub = modal.Stub("run-benchmark")


print("is_local() module", modal.is_local())


class FunctionParams(BaseModel):
    vendors: list[str] = []
    gpu_types: list[str] = []
    function_types: list[str] = []


@stub.function(
    image=image,
    secrets=[
        modal.Secret.from_dict({"DB_URL": "libsql://gpu-benchmark-viktorfa.turso.io"}),
        modal.Secret.from_name("benchmark-secrets"),
    ],
    schedule=modal.Period(hours=6),
    timeout=600,
)
async def my_function(args: FunctionParams = None):
    print("is_local() function", modal.is_local())
    print('os.getenv("DB_URL")', os.getenv("DB_URL"))
    print(f"args: {args}")

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

    hello_gpu_mystic = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://www.mystic.ai/v4/runs",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['MYSTIC_API_TOKEN']}",
            },
            json={
                "inputs": [
                    {
                        "type": "integer",
                        "value": 10,
                    },
                ],
                "pipeline": "vikfand/hello-gpu:v5",
                "async_run": False,
                "wait_for_resources": True,
            },
        ),
    )
    hello_torch_mystic = partial(
        run_web_function,
        request_f=partial(
            requests.post,
            url="https://www.mystic.ai/v4/runs",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['MYSTIC_API_TOKEN']}",
            },
            json={
                "inputs": [
                    {
                        "type": "integer",
                        "value": 5,
                    },
                ],
                "pipeline": "vikfand/hello-torch:v5",
                "async_run": False,
                "wait_for_resources": True,
            },
        ),
    )

    hello_gpu_replicate = partial(
        replicate.run,
        "viktorfa/hello-gpu:7ba7d6ce64dcaf85b0c1efb6e1168417c6c05b0b76a9217394e2a153be662dec",
        input={"number": 5},
    )
    hello_torch_replicate = partial(
        replicate.run,
        "viktorfa/hello-torch:3b297a2624682c11dfcbfd0aaecf9eebf14f2e8164069722cc733291ad5f22a0",
        input={"number": 5},
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
        {
            "vendor": "mystic",
            "gpu_type": "t4",
            "function_type": "hello_gpu",
            "function": hello_gpu_mystic,
        },
        {
            "vendor": "mystic",
            "gpu_type": "t4",
            "function_type": "hello_torch",
            "function": hello_torch_mystic,
        },
        {
            "vendor": "replicate",
            "gpu_type": "t4",
            "function_type": "hello_gpu",
            "function": hello_gpu_replicate,
        },
        {
            "vendor": "replicate",
            "gpu_type": "t4",
            "function_type": "hello_torch",
            "function": hello_torch_replicate,
        },
    ]

    if args:
        if args.vendors:
            configs = [config for config in configs if config["vendor"] in args.vendors]
        if args.gpu_types:
            configs = [
                config for config in configs if config["gpu_type"] in args.gpu_types
            ]
        if args.function_types:
            configs = [
                config
                for config in configs
                if config["function_type"] in args.function_types
            ]

    async with libsql_client.create_client(
        url=os.getenv("DB_URL") or "libsql://gpu-benchmark-viktorfa.turso.io",
        auth_token=os.getenv("TURSO_DATABASE_AUTH_TOKEN"),
    ) as client:
        db_client = client

        # vendors = await db_client.execute("SELECT DISTINCT * FROM vendors")
        # print("vendors", vendors.rows)

        print("Connected to db")

        print(f"Running {len(configs)} benchmarks")

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

    # result = my_function.remote(args=FunctionParams(vendors=["modal"]))

    print("result", result)


async def run_web_function(request_f: callable):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, request_f)

    print("result")
    print(result)

    if result.ok:
        return result.json()
    else:
        raise Exception(f"Error: {result.status_code} {result.reason}")


async def run_benchmark_wrapper(f: callable):
    is_coroutine = asyncio.iscoroutinefunction(f)
    loop = asyncio.get_running_loop()
    start_time = time.perf_counter()
    is_success = False
    error = None
    result = None
    try:
        if is_coroutine:
            result = await f()
        else:
            result = await loop.run_in_executor(None, f)
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
    print(f"Starting benchmark for {config['vendor']} {config['function_type']}")
    benchmark_result = await run_benchmark_wrapper(config["function"])
    print(
        f"Finished benchmark for {config['vendor']} {config['function_type']}, success: {benchmark_result['is_success']}"
    )
    error = benchmark_result.get("error")
    if error:
        print(f"Error: {error} for {config['vendor']} {config['function_type']}")

    # Insert the benchmark results into the database
    # Adapt the INSERT statement to match your database schema
    insert_result = await db_client.execute(
        "INSERT INTO function_runs (vendor, total_time_ms, run_time_ms, gpu_type, function_type, status, error) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id",
        [
            config["vendor"],
            round(benchmark_result["total_time_s"] * 1000),
            round(benchmark_result["run_time_s"] * 1000)
            if benchmark_result.get("run_time_s")
            else None,
            config["gpu_type"],
            config["function_type"],
            "SUCCESS" if benchmark_result["is_success"] else "FAILURE",
            error,
        ],
    )

    print(
        f"Inserted benchmark for {config['vendor']} {config['function_type']} with id {insert_result.last_insert_rowid}"
    )

    return benchmark_result
