""" Generic flexible validation step usable in the pipeline
"""

from typing import Any, Callable, Type, TypeVar, Union

from configmate.base import operators, registry

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
SpecT_contra = TypeVar("SpecT_contra", bound="ValidationSpec", contravariant=True)


class TypeValidator(operators.Operator[T_contra, T_co]):
    """A validator that can be used to validate ensure value."""


ValidationSpec = Union[Callable[[T_contra], T_co], Type[T_co]]
ValidatorFactoryMethod = Callable[[SpecT_contra], TypeValidator[T_contra, T_co]]


###
# factory for validation strategies
###
class TypeValidatorFactory(
    registry.StrategyRegistryMixin[ValidationSpec, ValidatorFactoryMethod]
):
    @classmethod
    def build_validator(
        cls, key: ValidationSpec[T_contra, Union[T_co, Any]]
    ) -> TypeValidator[T_contra, T_co]:
        return cls.get_first_match(key)(key)


###
# concrete validation steps
###
class FunctionValidator(TypeValidator[T_contra, T_co]):
    def __init__(self, validator_method: Callable[[T_contra], T_co]) -> None:
        super().__init__()
        self._method = validator_method

    def _transform(self, ctx: operators.Context, input_: Any) -> T_co:
        return self._method(input_)


###
# register strategies in order of priority
###
TypeValidatorFactory.register(callable, FunctionValidator)
