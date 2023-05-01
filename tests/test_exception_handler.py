import asyncio
import sys
import typing

import pytest

import aspreno


@pytest.fixture(autouse=True)
def teardown_method() -> None:
    sys.excepthook = sys.__excepthook__


@pytest.fixture
def handler() -> aspreno.ExceptionHandler:
    return aspreno.ExceptionHandler()


def test_relay_no_exception(handler: aspreno.ExceptionHandler) -> None:
    """
    See if relay raises an exception in case no exception have been raised.
    """
    with pytest.raises(RuntimeError, match="No exceptions have been caught."):
        handler.relay()


def test_relay(handler: aspreno.ExceptionHandler) -> None:
    """
    Test the relay method.
    """

    class SignalException(Exception):
        handle_called = False
        report_called = False

        def handle(self, **kwargs: typing.Any) -> None:
            self.handle_called = True

        def report(self, **kwargs: typing.Any) -> None:
            self.report_called = True

    try:
        raise SignalException()
    except SignalException as exception:
        handler.relay()
        assert exception.handle_called
        assert exception.report_called


@pytest.mark.asyncio
async def test_relay_async(handler: aspreno.ExceptionHandler) -> None:
    """
    Test the relay method using async methods.
    """

    class SignalException(Exception):
        handle_called = False
        report_called = False

        async def handle(self, **_: typing.Any) -> None:
            self.handle_called = True

        async def report(self, **_: typing.Any) -> None:
            self.report_called = True

    try:
        raise SignalException()
    except SignalException as exception:
        handler.relay()
        await asyncio.sleep(1)

        assert exception.handle_called
        assert exception.report_called


def test_ignore_exception() -> None:
    class SignalExceptionHandler(aspreno.ExceptionHandler):
        ignore_errors = [AttributeError]
        acknowledge = False

        def handle(self, error: BaseException, **kwargs: typing.Any) -> None:
            self.acknowledge = True

    exception_handler = SignalExceptionHandler()
    aspreno.register_global_handler(exception_handler)

    try:
        raise AttributeError("This is a test")
    except AttributeError as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)

    assert exception_handler.acknowledge is False
    assert exception_handler.should_report is False


@pytest.mark.asyncio
async def test_handle_async() -> None:
    class MyExceptionHandler(aspreno.ExceptionHandler):
        was_handle_called: bool = False

        async def handle(self, error: BaseException, **kwargs: typing.Any) -> None:
            self.was_handle_called = True

    handler = MyExceptionHandler()
    aspreno.register_global_handler(handler)

    try:
        raise ValueError("This is a test")
    except ValueError as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        await asyncio.sleep(1)
        assert handler.was_handle_called


def test_handle_exception(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        was_handle_called: bool = False

        def handle(self, **_: typing.Any) -> None:
            self.was_handle_called = True

    aspreno.register_global_handler(handler)

    try:
        raise MyException()
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        assert exception.was_handle_called


def test_handle_exception_argumented(handler: aspreno.ExceptionHandler) -> None:
    class MyException(aspreno.ArgumentedException):
        error: typing.Optional[BaseException] = None
        arg1: typing.Optional[str] = None
        arg2: typing.Optional[str] = None
        traceback: typing.Any = None

        def handle(self, arg1: str, *, arg2: str, traceback: typing.Any) -> None:
            self.error = self
            self.arg1 = arg1
            self.arg2 = arg2
            self.traceback = traceback

    aspreno.register_global_handler(handler)

    try:
        raise MyException(**{"arg1": "arg1", "arg2": "arg2"})
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        assert exception.error == exception
        assert exception.arg1 == "arg1"
        assert exception.arg2 == "arg2"
        assert exception.traceback is not None


def test_handle_no_kwargs(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        def handle(self, _: BaseException) -> None:
            pass

    with pytest.raises(
        TypeError, match="'MyException' does not allow kwargs in the 'handle' method."
    ):
        try:
            raise MyException()
        except MyException:
            handler.relay()


@pytest.mark.asyncio
async def test_handle_async_no_kwargs(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        async def handle(self, _: BaseException) -> None:
            pass

    with pytest.raises(
        TypeError, match="'MyException' does not allow kwargs in the 'handle' method."
    ):
        try:
            raise MyException()
        except MyException:
            handler.relay()


@pytest.mark.asyncio
async def test_handle_exception_argumented_async(handler: aspreno.ExceptionHandler) -> None:
    class MyException(aspreno.ArgumentedException):
        error: typing.Optional[BaseException] = None
        arg1: typing.Optional[str] = None
        arg2: typing.Optional[str] = None
        traceback: typing.Any = None

        async def handle(self, arg1: str, *, arg2: str, traceback: typing.Any) -> None:
            self.error = self
            self.arg1 = arg1
            self.arg2 = arg2
            self.traceback = traceback

    aspreno.register_global_handler(handler)

    try:
        raise MyException(**{"arg1": "arg1", "arg2": "arg2"})
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        await asyncio.sleep(1)
        assert exception.error == exception
        assert exception.arg1 == "arg1"
        assert exception.arg2 == "arg2"
        assert exception.traceback is not None


@pytest.mark.asyncio
async def test_handle_exception_async(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        was_handle_called: bool = False

        async def handle(self, **_: typing.Any) -> None:
            self.was_handle_called = True

    aspreno.register_global_handler(handler)

    try:
        raise MyException()
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        await asyncio.sleep(1)
        assert exception.was_handle_called


def test_report_exception(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        was_report_called: bool = False

        def report(self, **_: typing.Any) -> None:
            self.was_report_called = True

    aspreno.register_global_handler(handler)

    try:
        raise MyException()
    except MyException as exception:
        sys.excepthook(type(exception), exception, None)
        assert exception.was_report_called


@pytest.mark.asyncio
async def test_report_exception_async(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        was_report_called: bool = False

        async def report(self, **_: typing.Any) -> None:
            self.was_report_called = True

    aspreno.register_global_handler(handler)

    try:
        raise MyException()
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        await asyncio.sleep(1)
        assert exception.was_report_called


def test_report_no_kwargs(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        def report(self, _: BaseException) -> None:
            pass

    with pytest.raises(
        TypeError, match="'MyException' does not allow kwargs in the 'report' method."
    ):
        try:
            raise MyException()
        except MyException:
            handler.relay()


@pytest.mark.asyncio
async def test_report_async_no_kwargs(handler: aspreno.ExceptionHandler) -> None:
    class MyException(Exception):
        async def report(self, _: BaseException) -> None:
            pass

    with pytest.raises(
        TypeError, match="'MyException' does not allow kwargs in the 'report' method."
    ):
        try:
            raise MyException()
        except MyException:
            handler.relay()


def test_report_exception_argumented(handler: aspreno.ExceptionHandler) -> None:
    class MyException(aspreno.ArgumentedException):
        error: typing.Optional[BaseException] = None
        arg1: typing.Optional[str] = None
        arg2: typing.Optional[str] = None
        traceback: typing.Any = None

        def report(self, arg1: str, *, arg2: str, traceback: typing.Any) -> None:
            self.error = self
            self.arg1 = arg1
            self.arg2 = arg2
            self.traceback = traceback

    aspreno.register_global_handler(handler)

    try:
        raise MyException(**{"arg1": "arg1", "arg2": "arg2"})
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        assert exception.error == exception
        assert exception.arg1 == "arg1"
        assert exception.arg2 == "arg2"
        assert exception.traceback is not None


@pytest.mark.asyncio
async def test_report_exception_argumented_async(handler: aspreno.ExceptionHandler) -> None:
    class MyException(aspreno.ArgumentedException):
        error: typing.Optional[BaseException] = None
        arg1: typing.Optional[str] = None
        arg2: typing.Optional[str] = None
        traceback: typing.Any = None

        async def report(self, arg1: str, *, arg2: str, traceback: typing.Any) -> None:
            self.error = self
            self.arg1 = arg1
            self.arg2 = arg2
            self.traceback = traceback

    aspreno.register_global_handler(handler)

    try:
        raise MyException(**{"arg1": "arg1", "arg2": "arg2"})
    except MyException as exception:
        sys.excepthook(type(exception), exception, exception.__traceback__)
        await asyncio.sleep(1)
        assert exception.error == exception
        assert exception.arg1 == "arg1"
        assert exception.arg2 == "arg2"
        assert exception.traceback is not None
