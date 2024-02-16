import dataclasses
from typing import Any, Dict, List, Type, TypeVar

import pytest
from configmate_plugins import pydantic_validator

from configmate.components import validators

T = TypeVar("T")


###
# Types for testing
###
@dataclasses.dataclass
class DataClass:
    a: int
    b: int


def function_validator(_: Any) -> DataClass:
    """This should not trigger the factory to validate with pydantic."""
    return DataClass(a=1, b=2)


lambda_function_validator = lambda x: DataClass(a=1, b=2)  # noqa
###
# Tests
###


### Test the PydanticValidator directly
@pytest.mark.parametrize(
    "input_, type_, expected",
    [
        ((1, "2"), List[int], [1, 2]),
        ({"a": 1, "b": "2"}, Dict[str, int], {"a": 1, "b": 2}),
        ({"a": 1, "b": 2}, DataClass, DataClass(a=1, b=2)),
    ],
)
def test_pydantic_validator(
    input_: Any,
    type_: Type[T],
    expected: T,
) -> None:
    """Test that the PydanticValidator works as expected."""
    validated_obj = pydantic_validator.PydanticValidator(type_)(input_)
    assert validated_obj == expected


### Test the factory method for the PydanticValidator
@pytest.mark.parametrize(
    "input_, type_, expected",
    [
        ((1, "2"), List[int], [1, 2]),
        ({"a": 1, "b": "2"}, Dict[str, int], {"a": 1, "b": 2}),
        ({"a": 1, "b": 2}, DataClass, DataClass(a=1, b=2)),
        (None, function_validator, DataClass(a=1, b=2)),
        (None, lambda_function_validator, DataClass(a=1, b=2)),
    ],
)
def test_modified_factory(
    input_: Any,
    type_: Type[T],
    expected: T,
) -> None:
    """Test that the factory method for the PydanticValidator works
    as intended after adding the plugin
    """
    validator = validators.TypeValidatorFactory.build_validator(type_)
    validated_obj = validator(input_)
    assert validated_obj == expected
