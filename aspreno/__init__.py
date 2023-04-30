import copy
import sys
from importlib.metadata import distribution as __dist

from ._utils import log as _log
from .global_handler import ArgumentedException as ArgumentedException
from .global_handler import ExceptionHandler as ExceptionHandler

__version__ = __dist("aspreno").version
__author__ = __dist("aspreno").metadata["Author"]

__old_excepthook = None


def register_global_handler(handler: ExceptionHandler) -> None:
    global __old_excepthook
    _log.debug(f"Registering a global handler: {handler}")
    __old_excepthook = copy.copy(sys.excepthook)
    sys.excepthook = handler._global_handler  # pyright: reportPrivateUsage=false
    _log.debug(__old_excepthook)
    handler.old_excepthook = __old_excepthook


def reset_global_handler() -> None:
    global __old_excepthook
    _log.debug("Replacing global handler by default the old excepthook.")
    if __old_excepthook:
        sys.excepthook = __old_excepthook
        __old_excepthook = None
