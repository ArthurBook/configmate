import abc
from typing import TYPE_CHECKING, Callable, Literal, Sequence, TypeVar, Union

from configmate import base, commons

if TYPE_CHECKING:
    from configmate.interpolation import env_var_interpolation

T = TypeVar("T", bound=base.BaseInterpolator)


class InterpFactoryRegistry(
    base.FactoryRegistry[
        Union[
            Literal[None],
            base.BaseInterpolator,
            Callable[[str], str],
            Sequence[Callable[[str], str]],
            "env_var_interpolation.MissingPolicy",
        ],
        T,
    ]
):
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
def pass_through(interpolator: T) -> T:
    return interpolator


@InterpFactoryRegistry.register(commons.check_if_callable)
class FunctionInterpolator(ConstructedInterpolator):
    ...


@InterpFactoryRegistry.register(commons.check_if_callable_sequence)
class PipedInterpolator(ConstructedInterpolator):
    def __init__(self, interpolators: Sequence[Callable[[str], str]]) -> None:
        super().__init__(commons.Pipe(*interpolators))
