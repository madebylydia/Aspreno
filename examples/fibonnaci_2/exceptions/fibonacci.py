import typing

from aspreno import ArgumentedException


class FibonacciException(ArgumentedException):
    def handle(self: typing.Self, number: int, **kwargs: typing.Any):
        print(f"You have tried to give me '{number}', but Fibonacci doesn't like this one :(")
