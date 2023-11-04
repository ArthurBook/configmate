from typing import Any, Callable, Literal, Type, TypeVar, Union, overload

from configmate import _utils, base

T = TypeVar("T")
ValidationSpec = Union[Literal[None], Callable[[Any], T], Type, base.BaseValidator[T]]


# fmt: off
@overload
def construct_validator(spec: ValidationSpec[T]) -> base.BaseValidator[T]:
    """
    Construct a validator by invoking the `ValidatorFactoryRegistry`.
    - If spec is None, returns a no-op validator.
    - If spec is a callable, returns a validator applying the callable for validation.
    - If spec is a type, returns a validator using the type for instantiation and validation.
    - If spec is an existing validator, returns the same validator.
    """
@overload
def construct_validator(spec: Literal[None]) -> base.BaseValidator: ...
@overload
def construct_validator(spec: Callable[[Any], T]) -> base.BaseValidator[T]: ...
@overload
def construct_validator(spec: Type[T]) -> base.BaseValidator[T]: ...
@overload
def construct_validator(spec: base.BaseValidator[T]) -> base.BaseValidator[T]: ...
# fmt: on
def construct_validator(spec):
    return ValidatorFactoryRegistry.get_strategy(spec)(spec)


class ValidatorFactoryRegistry(
    base.BaseMethodStore[ValidationSpec[T], base.BaseValidator[T]]
):
    """Registry for validator factories."""


@ValidatorFactoryRegistry.register(_utils.check_if_none, rank=0)
class NoValidator(base.BaseValidator[T]):
    def validate(self, object_: T) -> T:
        return object_


@ValidatorFactoryRegistry.register(_utils.make_typecheck(base.BaseValidator), rank=1)
def passthrough(validator: base.BaseValidator[T]) -> base.BaseValidator[T]:
    return validator


@ValidatorFactoryRegistry.register(_utils.check_if_callable, rank=2)
class ValidatorFromCallable(base.BaseValidator[T]):
    def __init__(self, validation_function: Callable[[Any], T]) -> None:
        super().__init__()
        self._validation_function = validation_function

    def validate(self, object_: T) -> T:
        return self._validation_function(object_)
