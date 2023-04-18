from functools import lru_cache

from exceptions.fibonacci import FibonacciException

from aspreno import ExceptionHandler, register_global_handler


@lru_cache(None)
def fibonacci(num: int) -> int:
    if num < 0:
        raise FibonacciException("Fibonacci incorrect value", **{"number": num})

    elif num < 2:
        return num

    return fibonacci(num - 1) + fibonacci(num - 2)


register_global_handler(ExceptionHandler())

print(fibonacci(2))
print(fibonacci(-1))
