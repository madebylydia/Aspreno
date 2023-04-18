import sys
import types
import typing
from inspect import signature

from ._utils import TYPE_EXCEPTHOOK
from ._utils import log as _log


class ArgumentedException(Exception):
    """
    This class is the same as the builtin Exception class in Python, however, it allows keyword
    arguments to feed "handle" methods with arguments.
    """

    additional_args: dict[str, typing.Any]

    def __init__(self, *args: object, **kwargs: typing.Any) -> None:
        self.additional_args = kwargs
        super().__init__(*args)

    def get_kwargs_for_handle(self) -> dict[str, typing.Any]:
        return self.get_kwargs_for_method(getattr(self, "handle"))

    def get_kwargs_for_report(self) -> dict[str, typing.Any]:
        return self.get_kwargs_for_method(getattr(self, "report"))

    def get_kwargs_for_method(
        self, method: typing.Callable[..., typing.Any]
    ) -> dict[str, typing.Any]:
        method_signature = signature(method)

        kwargs: dict[str, typing.Any] = {
            argument_name: self.additional_args[argument_name]
            for argument_name in method_signature.parameters
            if argument_name in self.additional_args
        }

        return kwargs


class ExceptionHandler:
    ignore_errors: list[type[Exception]] = []

    old_excepthook: TYPE_EXCEPTHOOK | None = None

    def should_report(self, error: typing.Type[Exception]) -> bool:
        """Indicates if the exception handler should report the error.
        This is based on ignored errors.

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
        error_type: type[BaseException],
        value: BaseException,
        traceback: types.TracebackType | None,
    ) -> None:
        _log.debug(f"Received new error: {error_type}")
        if error_type in self.ignore_errors:
            _log.debug("Ignoring, error has been set to be ignored.")
            return

        _log.debug('Now being handed to "handle"')
        self.handle(value, **{"traceback": traceback})

    def relay(self) -> None:
        """
        Manually attempt to handle an error by calling this method.

        Returns
        """
        exceptions_info = sys.exc_info()

        if exceptions_info[0] is None:
            raise RuntimeError("No exceptions have been caught.")

        self._global_handler(*exceptions_info)

    def handle(self, error: BaseException, **kwargs: typing.Any) -> None:
        _log.debug(
            f"Error {error.__class__.__name__} is being treated by the default's Aspreno handler."
        )
        _log.debug(f"Given kwargs to handle: {kwargs}")

        handled = False
        # Attempt to call "handle" if available
        if getattr(error, "handle", None):
            _log.info(f"{error.__class__.__name__} has defined handle, letting it self-handle.")

            # Detect if the raised exception is an argumented exception.
            if isinstance(error, ArgumentedException):
                _log.debug("This is an ArgumentedException, obtaining additional kwargs.")
                # Obtain kwargs for the handle method.
                additional_kwargs = error.get_kwargs_for_handle()

                # Merge kwargs together
                kwargs |= additional_kwargs

            try:
                _log.debug(f"Final kwargs: {kwargs}")
                error.handle(
                    **kwargs
                )  # pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false
                handled = True
                _log.debug("Successfully handled. Continuing...")
            except TypeError as exception:
                # In case the exception has removed "**kwargs" in its signature, raise a new
                # exception to alert of this issue. Else raise the original exception.
                if str(exception).endswith("got an unexpected keyword argument 'traceback'"):
                    raise TypeError(
                        f"'{error.__class__.__name__}' does not allow kwargs in the 'handle' method."
                    ) from exception
                raise exception

        # In case the exception does not have a handle method, call the default excepthook.
        if not handled:
            # Obtain traceback
            traceback = kwargs.get("traceback") or sys.last_traceback

            # Return to the original excepthook.
            if self.old_excepthook:
                _log.debug("Passing error to custom excepthook.")
                self.old_excepthook(type(error), error, traceback)
            else:
                _log.debug("Passing error to sys.__excepthook__.")
                sys.__excepthook__(type(error), error, traceback)

        # Report exception
        if getattr(error, "report", None):
            _log.info(f"{error.__class__.__name__} has defined report, letting it report.")

            try:
                error.report(
                    **kwargs
                )  # pyright: reportGeneralTypeIssues=false, reportUnknownMemberType=false
            except TypeError as exception:
                if str(exception).endswith("got an unexpected keyword argument 'traceback'"):
                    raise TypeError(
                        f"'{error.__class__.__name__}' does not allow kwargs in the 'report' method."
                    ) from exception
                raise exception
