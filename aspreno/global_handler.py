import sys
import types
import typing

from ._utils import log as _log

_RT = typing.TypeVar("_RT")


class ExceptionHandler:
    ignore_errors: typing.List[typing.Type[Exception]] = []

    old_excepthook: typing.Optional[
        typing.Callable[
            [
                typing.Type[BaseException],
                BaseException,
                typing.Optional[types.TracebackType],
            ],
            typing.Any,
        ]
    ] = None

    def _should_ignore_error(self, error: typing.Type[BaseException]) -> bool:
        """Returns if the raised error should be ignored or not.

        Parameters
        ----------
        error : typing.Type[Exception]
            The raised exception

        Returns
        -------
        bool
            If the error should be ignored.
        """
        return error in self.ignore_errors

    def should_report(self, error: typing.Type[Exception]) -> bool:
        """Indicates if the exception handler should report the error.
        This is based on ignored errors.

        .. warning:: We do not check for instance

        Parameters
        ----------
        error : Type of :py:class:`Exception`
            The type of the exception that was raised.

        Returns
        -------
        bool
            True if should report error, or False if not.
        """
        return error not in self.ignore_errors

    def _global_handler(
        self,
        error_type: typing.Type[BaseException],
        value: BaseException,
        traceback: typing.Optional[types.TracebackType],
    ):
        _log.debug(f"Received new error: {error_type}")
        if self._should_ignore_error(error_type):
            _log.debug("Ignoring, error has been set to be ignored.")
            return

        _log.debug('Now being handed to "handle"')
        self.handle(value, **{"traceback": traceback})

    def handle(self, error: BaseException, **kwargs: typing.Any):
        _log.debug(
            f"Error {type(error)} is being treated by the default's Aspreno handler."
        )
        _log.info(f"Given kwargs to handle: {kwargs}")

        if getattr(error, "handle", None):
            _log.info(f"{type(error)} has defined handle, letting it self-handle.")
            error.handle(error, **kwargs)  # type: ignore
            return

        traceback = kwargs.get("traceback")
        if not traceback:
            _log.debug(
                "Traceback not found in kwargs, fetching from sys.last_traceback"
            )
            traceback = sys.last_traceback
            _log.debug(f"Found {traceback}")

        if self.old_excepthook:
            _log.info("Custom excepthook found, returning error to this excepthook.")
            self.old_excepthook(type(error), error, traceback)
        else:
            _log.info("Returning error to default sys.excepthook.")
            sys.__excepthook__(type(error), error, traceback)
        return
