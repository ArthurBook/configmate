""" Generic flexible interpolation steps usable in the pipeline
"""

import re
from typing import Callable, Iterable, Literal, Mapping, Set, TypeVar, Union, get_args
import warnings

from configmate.base import constants, exceptions, operators, registry

OnMissingSpec = Literal["error", "ignore", "warn"]
ON_MISSING_KEYS: Set[str] = set(get_args(OnMissingSpec))

InterpolatorSpec = Union[
    Callable[[str], str],
    OnMissingSpec,
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
    ###
    # handlers for missing environment variables
    ###
    @staticmethod
    def _throw_error_on_missing(missing_vars: Set[str]) -> None:
        err_str = f"Missing environment variables: {missing_vars}"
        raise exceptions.MissingEnvironmentVariable(err_str)

    @staticmethod
    def _warn_on_missing(missing_vars: Set[str]) -> None:
        warnings.warn(f"Missing environment variables: {missing_vars}")

    @staticmethod
    def _ignore_on_missing(missing_vars: Set[str]) -> None:
        del missing_vars

    ###
    #
    ###
    def __init__(
        self,
        pattern: re.Pattern = constants.BASH_VAR_PATTERN,
        substitutions: Mapping[str, str] = constants.ENVIRONMENT,
        missing_env_var_handler: Callable[[Set[str]], None] = _throw_error_on_missing,
    ) -> None:
        super().__init__()
        self._sub_pattern = pattern
        self._substitutions = substitutions
        self._on_missing = missing_env_var_handler

    def _transform(self, ctx: operators.Context, input_: str) -> str:
        missing_vars: Set[str] = set()

        def replacer(match: re.Match) -> str:
            nonlocal missing_vars
            env_var_name = match.group("variable")
            if (value := self._substitutions.get(env_var_name)) is not None:
                return value
            if (default := match.group("default_value")) is not None:
                return default
            missing_vars.add(env_var_name)
            return match.group(0)

        subbed_text = self._sub_pattern.sub(replacer, input_)
        if missing_vars:
            self._on_missing(missing_vars)

        return subbed_text

    @classmethod
    def from_sub_mapping(
        cls,
        substitutions: Mapping[str, str],
        on_missing: Callable[[Set[str]], None] = _throw_error_on_missing,
        pattern: re.Pattern = constants.BASH_VAR_PATTERN,
    ) -> "VariableInterpolator":
        return cls(pattern, substitutions, on_missing)

    @classmethod
    def from_on_missing(
        cls,
        on_missing: OnMissingSpec,
        substitutions: Mapping[str, str] = constants.ENVIRONMENT,
        pattern: re.Pattern = constants.BASH_VAR_PATTERN,
    ) -> "VariableInterpolator":
        if on_missing == "error":
            return cls(pattern, substitutions, cls._throw_error_on_missing)
        if on_missing == "warn":
            return cls(pattern, substitutions, cls._warn_on_missing)
        if on_missing == "ignore":
            return cls(pattern, substitutions, cls._ignore_on_missing)
        raise ValueError(f"Unknown on_missing value: {on_missing}")


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
def is_on_missing_spec(spec: InterpolatorSpec) -> bool:
    return isinstance(spec, str) and spec in ON_MISSING_KEYS


def is_mapping(s: InterpolatorSpec) -> bool:
    return isinstance(s, Mapping)


def is_iterable(s: InterpolatorSpec) -> bool:
    return isinstance(s, Iterable)


InterpolatorFactory.register(callable, FunctionalInterpolator)
InterpolatorFactory.register(is_on_missing_spec, VariableInterpolator.from_on_missing)
InterpolatorFactory.register(is_mapping, VariableInterpolator.from_sub_mapping)
InterpolatorFactory.register(is_iterable, InterpolatorChain.from_factory)
