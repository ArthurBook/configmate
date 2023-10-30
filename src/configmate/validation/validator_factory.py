from typing import Any, Callable, Optional, Type, TypeVar
from configmate import base, commons
from configmate.validation import validation_strategies as strategies

T = TypeVar("T")


class ValidatorFactoryRegistry(
    base.FactoryRegistry[Optional[Callable[..., T]], base.BaseValidator[T]],
):
    ...


@ValidatorFactoryRegistry.register(commons.check_if_none)
class NoValidator(base.BaseValidator[T]):
    def __init__(self, _: None) -> None:
        super().__init__()

    def validate(self, object_: T) -> T:
        return object_


@ValidatorFactoryRegistry.register(commons.always)
class StrategyBasedValidator(base.BaseValidator[T]):
    def __init__(self, type_: Type[T]) -> None:
        super().__init__()
        self._target_cls = type_

    def validate(self, object_: Any) -> T:
        validator_cls = strategies.ValidationStrategyRegistry.get_strategy(object_)
        return validator_cls(self._target_cls).validate(object_)
