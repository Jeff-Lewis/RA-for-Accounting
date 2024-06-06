import time

def time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.2f} seconds to execute.")
        return result
    return wrapper

@time_logger
def get_sum(a, b):
    return a + b

get_sum(1, 241423253)