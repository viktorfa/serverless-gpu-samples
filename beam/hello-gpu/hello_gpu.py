import re
import subprocess
import json
from beam import App, Runtime

app = App(name="hello-gpu", runtime=Runtime(gpu="T4"))


@app.run()
def run(**kwargs):
    print("🔮 This is running remotely on Beam!")
    print(f"🔮 Inputs: {kwargs}")

    has_gpu = check_gpu()
    print(f"🔮 has_gpu: {has_gpu}")

    number = kwargs.get("x", 0)
    return f"Your number is {number}! 🎉, has_gpu: {has_gpu}"


@app.rest_api()
def api(x: int):
    print("🔮 This is running remotely on Beam!")
    print(f"🔮 x: {x}")

    has_gpu = check_gpu()
    print(f"🔮 has_gpu: {has_gpu}")

    number = x
    return f"Your number is {number}! 🎉, has_gpu: {has_gpu}"


def check_gpu():
    try:
        # Try running `nvidia-smi` to list NVIDIA GPUs
        subprocess.check_output(["nvidia-smi"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # `nvidia-smi` is not found or an error occurred
        return False


def get_gpu_info():
    try:
        # Use subprocess.run() to capture both stdout and stderr
        completed_process = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=gpu_name,driver_version,memory.total",
                "--format=json",
            ],
            text=True,  # Ensure text (string) output
            capture_output=True,  # Capture both stdout and stderr
            check=True,  # Raise CalledProcessError for non-zero exit codes
        )

        # Parse the JSON output from stdout
        gpu_info = json.loads(completed_process.stdout)
        return gpu_info

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # `nvidia-smi` is not found or an error occurred
        print(e)
        if isinstance(e, subprocess.CalledProcessError):
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
        return check_gpu()


def get_basic_gpu_info():
    try:
        # Run nvidia-smi to get GPU details
        nvidia_smi_output = subprocess.check_output(["nvidia-smi"], text=True)

        # Initialize a dictionary to store GPU info
        gpu_info = {}

        gpu_names = re.findall(
            r"GeForce GTX \d+|Tesla [A-Z]\d+|Quadro \w+|RTX \w+", nvidia_smi_output
        )
        if gpu_names:
            gpu_info["gpu_names"] = gpu_names

        # Use regular expressions to extract information
        driver_version_match = re.search(r"Driver Version: (\S+)", nvidia_smi_output)
        if driver_version_match:
            gpu_info["driver_version"] = driver_version_match.group(1)

        gpu_name_match = re.search(r"(\d+MiB / \d+MiB)", nvidia_smi_output)
        if gpu_name_match:
            gpu_info["memory_usage"] = gpu_name_match.group(1)

        # Depending on the detail and format of nvidia-smi's output, you can extract more information here

        return gpu_info

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Handle errors if nvidia-smi command fails
        print(e)
        return check_gpu()


def get_system_info():
    system_info = {}

    # Get CPU information
    try:
        lscpu_output = subprocess.check_output(["lscpu"], text=True)
        # Extract CPU name
        match = re.search(r"Model name:\s+(.*)", lscpu_output)
        if match:
            system_info["cpu_model"] = match.group(1)
        # Extract number of CPUs
        match = re.search(r"^CPU\(s\):\s+(\d+)", lscpu_output, re.MULTILINE)
        if match:
            system_info["vcpus"] = int(match.group(1))
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        system_info["cpu_info_error"] = str(e)

    # Get RAM information
    try:
        meminfo_output = subprocess.check_output(["cat", "/proc/meminfo"], text=True)
        # Extract total memory
        match = re.search(r"MemTotal:\s+(\d+) kB", meminfo_output)
        if match:
            # Convert from kB to GB for readability
            system_info["total_ram_gb"] = int(match.group(1)) / (1024 * 1024)
        # Extract available memory
        match = re.search(r"MemAvailable:\s+(\d+) kB", meminfo_output)
        if match:
            # Convert from kB to GB for readability
            system_info["available_ram_gb"] = int(match.group(1)) / (1024 * 1024)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        system_info["ram_info_error"] = str(e)

    return system_info


def get_cgroup_info():
    cgroup_info = {}

    # Fetch CPU limit (in quota and period, to calculate the number of CPU cores effectively allocated)
    try:
        with open("/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us") as f:
            cpu_quota = int(f.read().strip())
        with open("/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us") as f:
            cpu_period = int(f.read().strip())

        # Calculate the number of CPUs allocated, -1 quota means no limit
        if cpu_quota > 0 and cpu_period > 0:
            cgroup_info["cpu_allocated"] = cpu_quota / cpu_period
        else:
            cgroup_info["cpu_allocated"] = "unlimited"
    except FileNotFoundError:
        cgroup_info["cpu_info"] = "Not available"

    # Fetch memory limit
    try:
        with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as f:
            memory_limit = int(f.read().strip())

        # Convert memory limit from bytes to GB, -1 or high value means no effective limit
        if memory_limit < 0 or memory_limit >= 1e15:  # Example threshold for "no limit"
            cgroup_info["memory_allocated_gb"] = "unlimited"
        else:
            cgroup_info["memory_allocated_gb"] = memory_limit / (
                1024**3
            )  # Convert bytes to GB
    except FileNotFoundError:
        cgroup_info["memory_info"] = "Not available"

    return cgroup_info
