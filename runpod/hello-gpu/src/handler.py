"""A template for a handler file."""

import runpod
from typing import TypedDict


class JobParam(TypedDict):
    id: str
    input: dict


def handler(job: JobParam):
    """
    This is the handler function for the job.
    """

    job_input = job["input"]
    name = job_input.get("x", "World")
    return f"Hello, {name}!"


runpod.serverless.start({"handler": handler})
