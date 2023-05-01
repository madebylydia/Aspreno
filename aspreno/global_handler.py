# mypy: disable-error-code="attr-defined"

import asyncio
import sys
import types
import typing
from inspect import iscoroutinefunction, signature

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
    ignore_errors: list[type[BaseException]] = []
    """
    A list of exceptions to ignore.
    If an exception has been set to be ignored, the "handle" method will not be called.
    """

    old_excepthook: TYPE_EXCEPTHOOK | None = None

    _last_exception: type[BaseException] | None = None
    """
    Store the last exception that has been received.

    .. warning::
       Because the last exception has been received, it does not mean it has been handled.
    """

    @property
    def should_report(self) -> bool:
        """
        Indicates if the exception handler should report the error.
        This is based on the last received exception.

        Returns
        -------
        bool
            True if the error should be reported, or False if not.
        """
        return self._last_exception not in self.ignore_errors

    def _global_handler(
        self,
        error_type: type[BaseException],
        value: BaseException,
        traceback: types.TracebackType | None,
    ) -> None:
        _log.debug(f"Received new error: {error_type}")
        self._last_exception = error_type
        if error_type in self.ignore_errors:
            _log.debug("Ignoring, error has been set to be ignored.")
            return

        _log.debug('Now being handed to "handle"')

        if iscoroutinefunction(self.handle):
            _log.debug("Async handle method detected, running in async mode.")
            loop = asyncio.get_running_loop()
            loop.create_task(self.handle(value, **{"traceback": traceback}))
        else:
            self.handle(value, **{"traceback": traceback})

    def relay(self) -> None:
        """
        Manually attempt to handle an error by calling this method.
        """
        exceptions_info = sys.exc_info()

        if exceptions_info[0] is None:
            raise RuntimeError("No exceptions have been caught.")

        self._global_handler(*exceptions_info)

    def handle(
        self, error: BaseException, **kwargs: typing.Any
    ) -> typing.Coroutine[None, None, None] | None:
        """
        Handles an exception.

        Parameters
        ----------
        error : BaseException
            The exception that was raised.
        **kwargs : Any
            Additional arguments that will be passed to the handle method.

        Returns
        -------
        typing.Coroutine[None, None, None] | None
            If the handle method is async, a coroutine is returned.
        """
        _log.debug(
            f"{error.__class__.__name__} is being treated by the default's Aspreno handler."
        )
        handled = False

        # Attempt to call "handle" if available
        if hasattr(error, "handle"):
            _log.info(f"{error.__class__.__name__} has defined handle, letting it self-handle.")
            handle_kwargs = kwargs.copy()

            # Detect if the raised exception is an argumented exception.
            if isinstance(error, ArgumentedException):
                _log.debug("This is an ArgumentedException, obtaining additional kwargs.")
                # Obtain kwargs for the handle method.
                additional_kwargs = error.get_kwargs_for_handle()

                # Merge kwargs together
                handle_kwargs |= additional_kwargs.copy()

            try:
                _log.debug("Final kwargs for handle: %s", handle_kwargs)
                if iscoroutinefunction(error.handle):
                    event_loop = asyncio.get_running_loop()
                    event_loop.create_task(error.handle(**handle_kwargs))
                else:
                    f = error.handle(**handle_kwargs)
                handled = True
            except TypeError as exception:
                # In case the exception has removed "**kwargs" in its signature, raise a new
                # exception to alert of this issue. Else raise the original exception.
                if str(exception).endswith("got an unexpected keyword argument 'traceback'"):
                    raise TypeError(
                        f"'{error.__class__.__name__}' does not allow kwargs in the 'handle' method."
                    ) from exception
                raise exception  # pragma:  no cover

        # In case the exception does not have a handle method, call the default excepthook.
        if not handled:
            # Obtain traceback
            traceback = kwargs.get("traceback") or getattr(sys, "last_traceback", None)

            # Return to the original excepthook.
            if self.old_excepthook:
                _log.debug("Passing error to custom excepthook.")
                self.old_excepthook(type(error), error, traceback)
            else:  # pragma: no cover
                _log.debug("Passing error to sys.__excepthook__.")
                sys.__excepthook__(type(error), error, traceback)

        # Report exception
        if getattr(error, "report", None):
            _log.info(f"{error.__class__.__name__} has defined report, letting it report.")

            report_kwargs = kwargs.copy()
            if isinstance(error, ArgumentedException):
                _log.debug("This is an ArgumentedException, obtaining additional kwargs.")
                additional_kwargs = error.get_kwargs_for_report()

                report_kwargs |= additional_kwargs

            try:
                _log.debug("Final kwargs for report: %s", report_kwargs)
                if iscoroutinefunction(error.report):
                    loop = asyncio.get_running_loop()
                    loop.create_task(error.report(**report_kwargs))
                else:
                    error.report(**report_kwargs)
            except TypeError as exception:
                if str(exception).endswith("got an unexpected keyword argument 'traceback'"):
                    raise TypeError(
                        f"'{error.__class__.__name__}' does not allow kwargs in the 'report' method."
                    ) from exception
                raise exception  # pragma: no cover

        return None
