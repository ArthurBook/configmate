import abc
from typing import Any, Collection, Mapping, Type, TypeVar

from configmate import base, commons
from configmate.validation import validator_factory

T = TypeVar("T")
U = TypeVar("U")


@validator_factory.ValidatorFactoryRegistry.register(commons.always, rank=-1)
class StrategyBasedValidator(base.BaseValidator[T]):
    def __init__(self, target_type_: Type[T]) -> None:
        super().__init__()
        self._target_cls = target_type_

    def validate(self, object_: Any) -> T:
        validator_cls = ValidationStrategyRegistry.get_strategy(object_)
        return validator_cls(self._target_cls).validate(object_)


### Strategies
class ValidationStrategy(base.BaseValidator[U]):
    def __init__(self, validate_to: Type[U]) -> None:
        super().__init__()
        self._validation_target = validate_to

    @abc.abstractmethod
    def validate(self, object_: Any) -> U:
        ...


class ValidationStrategyRegistry(base.BaseRegistry[T, Type[ValidationStrategy]]):
    ...


@ValidationStrategyRegistry.register(commons.make_typechecker(Collection))
class ValidateBySplat(ValidationStrategy[U]):
    def validate(self, object_: Any) -> U:
        return self._validation_target(*object_)


@ValidationStrategyRegistry.register(commons.make_typechecker(Mapping))
class ValidateByDoubleSplat(ValidationStrategy[U]):
    def validate(self, object_: Any) -> U:
        return self._validation_target(**object_)
