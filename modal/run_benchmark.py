import os
import modal
import asyncio
import libsql_client
import time
from functools import partial


image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("libsql-client")
    .pip_install("asyncio")
    .env({"HALT_AND_CATCH_FIRE": 0})
)

stub = modal.Stub("run-benchmark")

if modal.is_local():
    local_secret = modal.Secret.from_dict({"DB_URL": "libsql://127.0.0.1:8080?tls=0"})
else:
    local_secret = modal.Secret.from_dict(
        {"DB_URL": "libsql://gpu-benchmark-viktorfa.turso.io"}
    )


@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("benchmark-secrets")],
    schedule=modal.Period(hours=6),
)
async def my_function():
    hello_gpu_f = modal.Function.lookup("hello-gpu", "f")
    hello_gpu = partial(hello_gpu_f.remote, x=15)
    hello_torch_cls = modal.Cls.lookup("hello-torch", "Model")
    hello_torch_obj = hello_torch_cls()
    hello_torch = partial(hello_torch_obj.predict.remote, x=12)

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
    ]

    async with libsql_client.create_client(
        url=os.getenv("DB_URL") or "libsql://gpu-benchmark-viktorfa.turso.io",
        auth_token=os.getenv("TURSO_DATABASE_AUTH_TOKEN"),
    ) as client:
        db_client = client
        results = await asyncio.gather(
            *[run_and_record_result(db_client, config) for config in configs]
        )

        print(results)

    return "OK"


@stub.local_entrypoint()
def main():
    result = asyncio.run(my_function.local())
    # result = my_function.remote()

    print("result", result)


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
