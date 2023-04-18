import typing
import pytest

from aspreno import ExceptionHandler


@pytest.fixture()
def handler() -> ExceptionHandler:
    return ExceptionHandler()

class ExceptionSignalHandle(Exception):
    handle_called: bool = False

    def handle(self, **kwargs: typing.Any):
        self.handle_called = True

@pytest.fixture()
def signal_handle() -> ExceptionSignalHandle:
    return ExceptionSignalHandle()


class ExceptionSignalReport(Exception):
    report_called: bool = False

    def report(self, **kwargs: typing.Any):
        self.report_called = True

@pytest.fixture()
def signal_report() -> ExceptionSignalReport:
    return ExceptionSignalReport()


class ExceptionSignalHandleReport(ExceptionSignalHandle, ExceptionSignalReport):
    ...
    

@pytest.fixture()
def signal_handle_and_report() -> ExceptionSignalHandleReport:
    return ExceptionSignalHandleReport()


def test_relay_no_exception(handler: ExceptionHandler):
    """
    See if relay raises an exception in case no exception have been raised.
    """
    with pytest.raises(RuntimeError):
        handler.relay()


def test_relay(handler: ExceptionHandler, signal_handle_and_report: ExceptionSignalHandleReport):
    """
    Test the relay method.
    """
    try:
        raise signal_handle_and_report
    except ExceptionSignalHandleReport as exception:
        handler.relay()
        assert exception.handle_called
        assert exception.report_called


def test_handle():
    pass
