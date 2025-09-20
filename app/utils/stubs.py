import random


def fake_benchmark_result(model:str, prompt:str, runs:int) -> dict:
    DUMMY_BENCHMARK_RESULT = {
        "model": model,
        "prompt": prompt,
        "runs": runs,
        "avg": round(random.uniform(0, 10), 1),
        "min": round(random.uniform(0, 10), 1),
        "max": round(random.uniform(0, 10), 1),
        "std_dev": round(random.uniform(0, 10), 1),
    }
    return DUMMY_BENCHMARK_RESULT
