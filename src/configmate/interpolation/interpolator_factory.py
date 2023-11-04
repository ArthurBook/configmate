from typing import TYPE_CHECKING, Callable, Literal, Sequence, Union, overload

from configmate import _utils, base

if TYPE_CHECKING:
    from configmate.interpolation import env_var_interpolation

InterpolationSpec = Union[
    Literal[None],
    Callable[[str], str],
    Sequence[Callable[[str], str]],
    base.BaseInterpolator,
    "env_var_interpolation.MissingPolicy",
]


# fmt: off
@overload
def construct_interpolator(spec: InterpolationSpec) -> base.BaseInterpolator:
    """
    Construct a interpolator by invoking the `interpolatorFactoryRegistry`.
    - If spec is None, returns a no-op interpolator.
    - If spec is a callable, use the callable for interpolation.
    - If spec is a sequence of callables, apply them in the given sequence.
    - If spec is an existing interpolator, returns the same interpolator.
    """
@overload
def construct_interpolator(spec: Literal[None]) -> base.BaseInterpolator: ...
@overload
def construct_interpolator(spec: Callable[[str], str]) -> base.BaseInterpolator: ...
@overload
def construct_interpolator(spec: Sequence[Callable[[str], str]]) -> base.BaseInterpolator: ...
@overload
def construct_interpolator(spec: base.BaseInterpolator) -> base.BaseInterpolator: ...
# fmt: on
def construct_interpolator(spec):
    return InterpolatorFactoryRegistry.get_strategy(spec)(spec)


class InterpolatorFactoryRegistry(
    base.BaseMethodStore[InterpolationSpec, base.BaseInterpolator]
):
    """Registry for interpolator factories."""


@InterpolatorFactoryRegistry.register(_utils.check_if_none, rank=0)
class EmptyInterpolator(base.BaseInterpolator):
    def interpolate(self, text: str) -> str:
        return text


@InterpolatorFactoryRegistry.register(
    _utils.make_typecheck(base.BaseInterpolator), rank=1
)
def pass_through(interpolator: base.BaseInterpolator) -> base.BaseInterpolator:
    return interpolator


@InterpolatorFactoryRegistry.register(_utils.check_if_callable, rank=2)
class FunctionInterpolator(base.BaseInterpolator):
    def __init__(self, strategy: Callable[[str], str]) -> None:
        super().__init__()
        self._strategy = strategy

    def interpolate(self, text: str) -> str:
        return self._strategy(text)


@InterpolatorFactoryRegistry.register(_utils.check_if_callable_sequence, rank=3)
class PipedInterpolator(base.BaseInterpolator):
    def __init__(self, interpolators: Sequence[Callable[[str], str]]) -> None:
        self._strategy = _utils.Pipe(*interpolators)

    def interpolate(self, text: str) -> str:
        return self._strategy(text)
