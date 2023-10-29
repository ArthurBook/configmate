import abc
from typing import Callable, Literal, Sequence, TypeVar

from configmate import base, commons
from configmate.interpolation import env_var_interpolation as env_interp

T = TypeVar(
    "T",
    Literal[None],
    base.BaseInterpolator,
    Callable[[str], str],
    Sequence[Callable[[str], str]],
    env_interp.MissingPolicy,
)

U = TypeVar("U", bound=base.BaseInterpolator)


class InterpFactoryRegistry(base.BaseFactoryRegistry[T, base.BaseInterpolator]):
    """Registry for interpolator factories."""


class ConstructedInterpolator(base.BaseInterpolator, abc.ABC):
    def __init__(self, strategy: Callable[[str], str]) -> None:
        super().__init__()
        self.strategy = strategy

    def interpolate(self, text: str) -> str:
        return self.strategy(text)


@InterpFactoryRegistry.register(commons.check_if_none)
class EmptyInterpolator(ConstructedInterpolator):
    def __init__(self, _: Literal[None]) -> None:
        super().__init__(lambda x: x)


@InterpFactoryRegistry.register(commons.make_typechecker(base.BaseInterpolator))
def pass_through(interpolator: U) -> U:
    return interpolator


@InterpFactoryRegistry.register(commons.check_if_callable)
class FunctionInterpolator(ConstructedInterpolator):
    ...


@InterpFactoryRegistry.register(commons.check_if_callable_sequence)
class PipedInterpolator(ConstructedInterpolator):
    def __init__(self, interpolators: Sequence[Callable[[str], str]]) -> None:
        super().__init__(commons.Pipe(*interpolators))


@InterpFactoryRegistry.register(commons.make_typechecker(env_interp.MissingPolicy))
def make_env_interpolator(mode: env_interp.MissingPolicy) -> env_interp.EnvInterpolator:
    return env_interp.EnvInterpolator(handling=mode)
