import aspreno
import typing
import sys


class AsprenoTestGlobalHandler(aspreno.ExceptionHandler):
    
    def handle(self, error: BaseException, **kwargs: typing.Any):
        return super().handle(error, **kwargs)


def test_register_global_handler():
    my_global_handler = AsprenoTestGlobalHandler()
    
    aspreno.register_global_handler(my_global_handler)
    assert sys.excepthook == my_global_handler._global_handler  # pyright: reportPrivateUsage=false


def test_register_global_handler_with_custom_excepthook():
    custom_excepthook = lambda x, y, z : print(x, y, z)  # pyright: reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportUnknownVariableType=false

    sys.excepthook = custom_excepthook
    
    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)

    assert global_handler.old_excepthook == custom_excepthook


def test_reset_global_handler():
    sys.excepthook = sys.__excepthook__

    # Ensure we are using sys.__excepthook__ first, or it's an immediate fail
    assert sys.excepthook == sys.__excepthook__

    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)
    
    aspreno.reset_global_handler()
    
    assert sys.excepthook == sys.__excepthook__


def test_reset_global_handler_with_custom_excepthook():
    custom_excepthook = lambda x, y, z : print(x, y, z)  # pyright: reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportUnknownVariableType=false

    sys.excepthook = custom_excepthook
    
    global_handler = AsprenoTestGlobalHandler()
    aspreno.register_global_handler(global_handler)
    
    aspreno.reset_global_handler()
    assert sys.excepthook == custom_excepthook
