import abc
from typing import Any, Collection, Mapping, Type, TypeVar

from configmate import base, commons

T = TypeVar("T")
U = TypeVar("U")


class ValidationStrategy(base.BaseValidator[U]):
    def __init__(self, validate_to: Type[U]) -> None:
        super().__init__()
        self._validation_target = validate_to

    @abc.abstractmethod
    def validate(self, object_: Any) -> U:
        ...


class ValidationStrategyRegistry(base.BaseRegistry[T, Type[ValidationStrategy]]):
    ...


### Implementations
@ValidationStrategyRegistry.register(commons.make_typechecker(Collection))
class ValidateBySplat(ValidationStrategy[U]):
    def validate(self, object_: Any) -> U:
        return self._validation_target(*object_)


@ValidationStrategyRegistry.register(commons.make_typechecker(Mapping))
class ValidateByDoubleSplat(ValidationStrategy[U]):
    def validate(self, object_: Any) -> U:
        return self._validation_target(**object_)
