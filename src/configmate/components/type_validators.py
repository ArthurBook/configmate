""" Generic flexible validation step usable in the pipeline
"""
from typing import Any, Callable, Generic, Type, TypeVar, Union

from configmate.common import context, registry, transformations, types

T = TypeVar("T")
U = TypeVar("U", bound="ValidationSpec")
V = TypeVar("V")


class TypeValidator(transformations.Transformer[Any, T], Generic[T]):
    """A validator that can be used to validate ensure value."""


ValidationSpec = Union[Callable[[Any], T], Type[T]]
TypeValidatorFactoryMethod = Callable[[U], TypeValidator[T]]


###
# factory for validation strategies
###
class TypeValidatorFactory(
    registry.StrategyRegistryMixin[ValidationSpec[U], TypeValidatorFactoryMethod[U, T]],
    types.RegistryProtocol[ValidationSpec[U], TypeValidator[T]],
):
    def __getitem__(self, key: ValidationSpec[V]) -> TypeValidator[V]:
        return self.get_first_match(key)(key)  # type: ignore


###
# concrete validation steps
###
class FunctionValidator(TypeValidator[T]):
    def __init__(self, validator_method: Callable[[Any], T]) -> None:
        super().__init__()
        self._method = validator_method

    def _apply(self, ctx: context.Context, input_: Any) -> T:
        return self._method(input_)


class ClassValidator(TypeValidator[T]):
    def __init__(self, class_: Type[T]) -> None:
        super().__init__()
        self._cls = class_
        self.output_type = class_

    def _apply(self, ctx: context.Context, input_: Any) -> T:
        return self._cls(input_)  # type: ignore


###
# register strategies in order of priority
###
# fmt: off
TypeValidatorFactory.register(callable, FunctionValidator)
TypeValidatorFactory.register(lambda spec: isinstance(spec, type), ClassValidator) # type: ignore
# fmt: on
