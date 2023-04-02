import sys
from importlib.metadata import distribution as __dist

from ._utils import log as _log
from .global_handler import ExceptionHandler

__version__ = __dist("aspreno").version
__author__ = __dist("aspreno").metadata["Author"]

__old_excepthook = None


def register_global_handler(handler: ExceptionHandler):
    global __old_excepthook
    _log.debug(f"Registering a global handler: {handler}")
    __old_excepthook = sys.excepthook
    sys.excepthook = handler._global_handler  # pyright: reportPrivateUsage=false
    if __old_excepthook != sys.__excepthook__:
        _log.debug("Custom excepthook found, now passing it to the handler.")
        handler.old_excepthook = __old_excepthook


def reset_global_handler():
    global __old_excepthook
    _log.debug("Replacing global handler by default the old excepthook.")
    if __old_excepthook:
        sys.excepthook = __old_excepthook
