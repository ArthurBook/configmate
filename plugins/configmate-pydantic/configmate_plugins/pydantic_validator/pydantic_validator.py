""" Pydantic Validator
"""

from typing import Any, Type, TypeVar

import pydantic

from configmate.base import operators
from configmate.components import validators

T = TypeVar("T")


class PydanticValidator(validators.TypeValidator[Any, T]):
    def __init__(self, type_: Type[T]) -> None:
        super().__init__()
        self._type = type_

    def _transform(self, ctx: operators.Context, input_: Any) -> T:
        return validate_with_pydantic(self._type, input_)


def validate_with_pydantic(type_: Type[T], obj: Any) -> T:
    class Validator(pydantic.BaseModel):
        """Temporary class to validate the object with pydantic."""

        object: type_

    return Validator(object=obj).object


###
# Register the validator with configmate
###
def is_not_function(obj: Any) -> bool:
    return not isinstance(obj, type(is_not_function))


validators.TypeValidatorFactory.register(
    is_not_function,
    PydanticValidator,
    where="first",
)
## NOTE: we want this to trigger for everything except functions
