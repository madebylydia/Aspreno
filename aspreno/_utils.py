import logging
import sys
import types
from typing import Any, Callable, Optional, Type

if sys.version_info < (3, 10):
    # 3.8, 3.9
    from typing_extensions import TypeAlias  # pragma: no cover
else:
    # 3.10, 3.11
    from typing import TypeAlias  # pragma: no cover


TYPE_EXCEPTHOOK: TypeAlias = Callable[
    [
        Type[BaseException],
        BaseException,
        Optional[types.TracebackType],
    ],
    Any,
]

log = logging.getLogger("aspreno")
