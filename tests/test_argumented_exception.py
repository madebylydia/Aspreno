import pytest

from aspreno import ArgumentedException

ARGS = {"argument_1": "I exist", "argument_2": 100, "argument_3": {"hello": "world"}}


class MyArgumentedException(ArgumentedException):
    def handle(self, argument_1: str, argument_2: int, *, argument_3: dict[str, str]):
        pass


def test_additional_args():
    exception = MyArgumentedException("This error is being raised", **ARGS)

    assert exception.additional_args == ARGS


def test_obtain_kwargs_for_method():
    exception = MyArgumentedException("This error is being raised", **ARGS)

    def my_method(argument_1: str):
        pass

    assert exception.get_kwargs_for_method(my_method) == {"argument_1": ARGS["argument_1"]}

    def my_method_2(*, argument_2: str):
        pass

    assert exception.get_kwargs_for_method(my_method_2) == {"argument_2": ARGS["argument_2"]}


def test_obtain_kwargs_for_handle():
    exception = MyArgumentedException("This error is being raised", **ARGS)

    assert exception.get_kwargs_for_handle() == ARGS

    class MySecondArgumentedException(ArgumentedException):
        pass

    exception = MySecondArgumentedException("This error is being raised", **ARGS)
    with pytest.raises(AttributeError):
        exception.get_kwargs_for_handle()
