import typing
from functools import lru_cache

from aspreno import ExceptionHandler, register_global_handler


class FibonacciHandler(ExceptionHandler):
    def handle(self, error: BaseException, **kwargs: typing.Any) -> None:
        if isinstance(error, ValueError) and str(error) == "Fibonacci Incorrect value":
            print("You have given a number that cannot be worked upon Fibonacci sequence!")

        # Default handle's method
        super().handle(error, **kwargs)


@lru_cache(None)
def fibonacci(num: int) -> int:
    if num < 0:
        raise ValueError("Fibonacci Incorrect value")

    elif num < 2:
        return num

    return fibonacci(num - 1) + fibonacci(num - 2)


handler = FibonacciHandler()
register_global_handler(handler)

print(fibonacci(1))
print(fibonacci(-1))
