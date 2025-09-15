import time
import functools


def exponential_retry_wrapper(func):
    """
    Декоратор для экспоненциального retry
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + 1
                    time.sleep(wait_time)
                    continue
                else:
                    raise

    return wrapper
