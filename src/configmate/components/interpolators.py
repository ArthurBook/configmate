""" Generic flexible interpolation steps usable in the pipeline
"""
import contextlib
import re
from typing import Callable, Iterable, Mapping, Set, TypeVar, Union

from configmate.base import constants, operators, registry

InterpolatorSpec = Union[
    Callable[[str], str],
    Mapping[str, str],
    Iterable["InterpolatorSpec"],
]
_SpecT_co = TypeVar("_SpecT_co", bound=InterpolatorSpec, covariant=True)
InterpolatorFactoryMethod = Callable[[_SpecT_co], "StringInterpolator"]


###
# base class for interpolation steps
###
class StringInterpolator(operators.Operator[str, str]):
    input_type = str
    output_type = str


###
# factory for validation strategies
###
class InterpolatorFactory(
    registry.StrategyRegistryMixin[InterpolatorSpec, InterpolatorFactoryMethod],
):
    @classmethod
    def build_interpolator(cls, key: InterpolatorSpec) -> StringInterpolator:
        return cls.get_first_match(key)(key)


###
# concrete interpolation steps
###
class FunctionalInterpolator(StringInterpolator):
    def __init__(self, interpolation_method: Callable[[str], str]) -> None:
        super().__init__()
        self._method = interpolation_method

    def _transform(self, ctx: operators.Context, input_: str) -> str:
        return self._method(input_)


class VariableInterpolator(StringInterpolator):
    def __init__(
        self,
        substitutions: Mapping[str, str] = constants.ENVIRONMENT,
        pattern: re.Pattern = constants.BASH_VAR_PATTERN,
    ) -> None:
        super().__init__()
        self._substitutions = substitutions
        self._sub_pattern = pattern

    def _transform(self, ctx: operators.Context, input_: str) -> str:
        missing_vars: Set[str] = set()

        def replacer(match: re.Match) -> str:
            nonlocal missing_vars
            env_var_name = match.group("variable")
            with contextlib.suppress(KeyError):
                return self._substitutions[env_var_name]
            missing_vars.add(env_var_name)
            return match.group("default_value") or match.group(0)

        ctx[self].missing_vars = missing_vars
        return self._sub_pattern.sub(replacer, input_)


class InterpolatorChain(StringInterpolator):
    build_interpolator = InterpolatorFactory.build_interpolator

    def __init__(self, interpolators: Iterable[operators.Operator[str, str]]) -> None:
        super().__init__()
        if not (interpolators := list(interpolators)):
            raise ValueError("At least one interpolator is required for a chain.")
        self._interpolation = interpolators.pop(0)
        for interpolator in interpolators:
            self._interpolation = self._interpolation.pipe_to(interpolator)

    def _transform(self, ctx: operators.Context, input_: str) -> str:
        return self._interpolation(input_, ctx)

    @classmethod
    def from_factory(cls, spec: Iterable[InterpolatorSpec]) -> "InterpolatorChain":
        spec = list(spec)  # ensures we dont exhaust the iterator
        if all(callable(s) or isinstance(s, Mapping) for s in spec):
            return cls(map(cls.build_interpolator, spec))
        raise ValueError("Only callables and maps supported for chained interpolation.")


###
# register concrete interpolation steps in order of preference
###
# fmt: off
InterpolatorFactory.register(callable, FunctionalInterpolator)
InterpolatorFactory.register(lambda s: isinstance(s, Mapping), VariableInterpolator)
InterpolatorFactory.register(lambda s: isinstance(s, Iterable), InterpolatorChain.from_factory)
# fmt: on
