import time
from typing import Callable
import statistics


def calculate_latency_stats(model:str, prompt:str, runs:int, func: Callable[[], dict]) -> dict:
    latencies = []
    for i in range(runs):
        data = func()
        latencies.append(data.get("latency_seconds"))
        time.sleep(30)

    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    std_dev = statistics.stdev(latencies)

    result = {
        "model": model,
        "prompt": prompt,
        "runs": runs,
        "avg": avg_latency,
        "min": min_latency,
        "max": max_latency,
        "std_dev": std_dev
    }
    return result
