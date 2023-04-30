import pytest

from aspreno import ArgumentedException

ARGS = {"argument_1": "I exist", "argument_2": 100, "argument_3": {"hello": "world"}}


class MyArgumentedException(ArgumentedException):
    async def handle(
        self, argument_1: str, argument_2: int, *, argument_3: dict[str, str]
    ) -> None:
        pass

    async def report(
        self, argument_1: str, argument_2: int, *, argument_3: dict[str, str]
    ) -> None:
        pass


@pytest.fixture()
def argumented_exception() -> MyArgumentedException:
    return MyArgumentedException("This error is being raised", **ARGS)


def test_additional_args(argumented_exception: MyArgumentedException) -> None:
    """
    Test that the additional args are stored correctly
    """
    assert argumented_exception.additional_args == ARGS


def test_obtain_kwargs_for_method(argumented_exception: MyArgumentedException) -> None:
    """
    Test that methods are correctly introspected.
    """

    def my_method(argument_1: str) -> None:
        pass

    assert argumented_exception.get_kwargs_for_method(my_method) == {
        "argument_1": ARGS["argument_1"]
    }

    def my_method_2(*, argument_2: str) -> None:
        pass

    assert argumented_exception.get_kwargs_for_method(my_method_2) == {
        "argument_2": ARGS["argument_2"]
    }


def test_obtain_kwargs_for_handle(argumented_exception: MyArgumentedException) -> None:
    """
    Test that the handle method is correctly introspected.
    """
    assert argumented_exception.get_kwargs_for_handle() == ARGS

    class SecondArgumentedException(ArgumentedException):
        pass

    exception = SecondArgumentedException("This error is being raised", **ARGS)
    with pytest.raises(AttributeError):
        exception.get_kwargs_for_handle()


def test_obtain_kwargs_for_report(argumented_exception: MyArgumentedException) -> None:
    """
    Test that the report method is correctly introspected.
    """
    assert argumented_exception.get_kwargs_for_report() == ARGS

    class SecondArgumentedException(ArgumentedException):
        pass

    exception = SecondArgumentedException("This error is being raised", **ARGS)
    with pytest.raises(AttributeError):
        exception.get_kwargs_for_report()
