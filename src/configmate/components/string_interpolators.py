""" Generic flexible interpolation steps usable in the pipeline
"""
import contextlib
import os
import re
from typing import Callable, Iterable, Mapping, Optional, TypeVar, Union

from configmate.common import context, registry, transformations, types


T = TypeVar("T")
U = TypeVar("U", bound="InterpolatorSpec")

# fmt: off
InterpolatorSpec = Union[Mapping[str, str], Callable[[str], str], Iterable["InterpolatorSpec"]]
InterpolatorFactoryMethod = Callable[[U], "StringInterpolator"]
# fmt: on


###
# base class for interpolation steps
###
class StringInterpolator(transformations.Transformer[str, str]):
    input_type = str
    output_type = str


###
# factory for validation strategies
###
class InterpolatorFactory(
    registry.StrategyRegistryMixin[InterpolatorSpec, InterpolatorFactoryMethod],
    types.RegistryProtocol[InterpolatorSpec, StringInterpolator],
):
    def __getitem__(self, key: InterpolatorSpec) -> StringInterpolator:
        return self.get_first_match(key)(key)


###
# concrete interpolation steps
###
class FunctionalInterpolator(StringInterpolator):
    def __init__(self, interpolation_method: Callable[[str], str]) -> None:
        super().__init__()
        self._method = interpolation_method

    def _apply(self, ctx: context.Context, input_: str) -> str:
        return self._method(input_)


class EnvironmentVariables(types.RegistryProtocol):
    def __getitem__(self, key: str) -> Optional[str]:
        return os.environ[key]


class VariableInterpolator(StringInterpolator):
    DEFAULT_SUB_PATTERN = r"\${(?P<variable>\w+)(?::(?P<default_value>[^}:]+))?}"
    MISSING_ENV_VARS_CONTEXT_KEY = "missing_vars"

    def __init__(
        self,
        variables: types.RegistryProtocol[str, str] = EnvironmentVariables(),
        pattern: re.Pattern = re.compile(DEFAULT_SUB_PATTERN),
    ) -> None:
        super().__init__()
        self._variables = variables
        self._pattern = pattern

    def _apply(self, ctx: context.Context, input_: str) -> str:
        missing_vars = ctx[self.MISSING_ENV_VARS_CONTEXT_KEY] = set()

        def replacer(match: re.Match) -> str:
            nonlocal missing_vars
            env_var_name = match.group("variable")
            with contextlib.suppress(KeyError):
                return self._variables[env_var_name]
            missing_vars.add(env_var_name)
            return match.group("default_value") or match.group(0)

        return self._pattern.sub(replacer, input_)


class InterpolatorChain(StringInterpolator):
    factory = InterpolatorFactory()

    def __init__(
        self, interpolators: Iterable[transformations.Transformer[str, str]]
    ) -> None:
        super().__init__()
        if not (interpolators := list(interpolators)):
            raise ValueError("At least one interpolator is required for a chain.")
        self._interpolation = interpolators[0]
        for interpolator in interpolators[1:]:
            self._interpolation += interpolator

    def _apply(self, ctx: context.Context, input_: str) -> str:
        return self._interpolation(input_, ctx)

    @classmethod
    def from_factory(cls, spec: Iterable[InterpolatorSpec]) -> "InterpolatorChain":
        spec = list(spec)  # ensures we dont exhaust the iterator
        if all(callable(s) or isinstance(s, Mapping) for s in spec):
            return cls(map(cls.factory.__getitem__, spec))
        raise ValueError("Only callables and maps supported for chained interpolation.")


###
# register concrete interpolation steps in order of preference
###
# fmt: off
InterpolatorFactory.register(callable, FunctionalInterpolator)
InterpolatorFactory.register(lambda s: isinstance(s, Mapping), VariableInterpolator)
InterpolatorFactory.register(lambda s: isinstance(s, Iterable), InterpolatorChain.from_factory)
# fmt: on
