import logging
import sys
import types
import typing

import aspreno


class AsprenoTestGlobalHandler(aspreno.ExceptionHandler):
    async def handle(self, error: BaseException, **kwargs: typing.Any) -> None:
        super().handle(error, **kwargs)


def test_register_global_handler() -> None:
    my_global_handler = AsprenoTestGlobalHandler()

    aspreno.register_global_handler(my_global_handler)
    assert sys.excepthook == my_global_handler._global_handler  # pyright: reportPrivateUsage=false


def test_register_global_handler_with_custom_excepthook() -> None:
    custom_excepthook = lambda x, y, z: print(
        x, y, z
    )  # pyright: reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportUnknownVariableType=false

    sys.excepthook = custom_excepthook

    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)

    assert global_handler.old_excepthook == custom_excepthook


def test_reset_global_handler() -> None:
    sys.excepthook = sys.__excepthook__

    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)
    assert sys.excepthook == global_handler._global_handler

    aspreno.reset_global_handler()
    assert sys.excepthook == sys.__excepthook__


def test_reset_global_handler_with_custom_excepthook() -> None:
    was_called = False

    def custom_excepthook(
        error_type: type[BaseException],
        value: BaseException,
        traceback: types.TracebackType | None,
    ) -> None:
        logging.getLogger("aspreno").debug("NONPACKAGE: Custom excepthook called")
        nonlocal was_called
        was_called = True

    sys.excepthook = custom_excepthook

    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)
    aspreno.reset_global_handler()

    assert sys.excepthook == custom_excepthook

    sys.excepthook(*sys.exc_info())  # pyright: ignore
    assert was_called
