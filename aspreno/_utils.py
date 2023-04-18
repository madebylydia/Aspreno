import logging
import types
import typing

TYPE_EXCEPTHOOK: typing.TypeAlias = typing.Callable[
    [
        type[BaseException],
        BaseException,
        types.TracebackType | None,
    ],
    typing.Any,
]

log = logging.getLogger("aspreno")
