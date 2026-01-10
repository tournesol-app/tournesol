from typing import Callable

def threading(max_workers: int, thread_function: Callable, *args_lists) -> list:
    if max_workers == 1:
        return [thread_function(*args) for args in zip(*args_lists)]
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers) as e:
        return list(e.map(thread_function, *args_lists))
    