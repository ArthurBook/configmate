from typing import Any, Callable, Optional, TypeVar

from configmate import base, commons

T = TypeVar("T")


class ValidatorFactoryRegistry(
    base.FactoryRegistry[Optional[Callable[[Any], T]], base.BaseValidator[T]]
):
    """Registry for validator factories."""


@ValidatorFactoryRegistry.register(commons.check_if_none, rank=0)
class NoValidator(base.BaseValidator[T]):
    def validate(self, object_: T) -> T:
        return object_
