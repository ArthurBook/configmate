from typing import Callable, Generic, Sequence, TypeVar, Union, overload

from configmate import _utils, base

T = TypeVar("T")
AggregatorSpec = Union[Callable[[Sequence[T]], T], base.BaseAggregator]


# fmt: off
@overload
def construct_aggregator(spec: AggregatorSpec) -> base.BaseAggregator:
    """
    Construct a aggregator by invoking the `AggregatorFactoryRegistry`.
    - If spec is a callable, use the callable for aggregation.
    - If spec is an existing aggregator, returns the same aggregator.
    """
@overload
def construct_aggregator(spec: Callable[[Sequence[T]], T]) -> base.BaseAggregator: ...
@overload
def construct_aggregator(spec: base.BaseAggregator) -> base.BaseAggregator: ...
# fmt: on
def construct_aggregator(spec):
    return AggregatorFactoryRegistry.get_strategy(spec)(spec)


class AggregatorFactoryRegistry(
    base.BaseMethodStore[AggregatorSpec, base.BaseAggregator]
):
    """Registry for aggregator factories."""


@AggregatorFactoryRegistry.register(_utils.make_typecheck(base.BaseAggregator), rank=0)
def pass_through(aggregator: base.BaseAggregator) -> base.BaseAggregator:
    return aggregator


@AggregatorFactoryRegistry.register(callable, rank=1)
class FunctionalAggregator(base.BaseAggregator, Generic[T]):
    def __init__(self, function_: Callable[[Sequence[T]], T]) -> None:
        self._backend = function_

    def aggregate(self, sequence: Sequence[T]) -> T:
        return self._backend(sequence)
