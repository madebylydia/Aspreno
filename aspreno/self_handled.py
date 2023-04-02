import typing


class SelfHandleable(BaseException):
    def handle(self: typing.Self, *args: typing.Any, **kwargs: typing.Any):
        ...
