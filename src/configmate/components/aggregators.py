""" Generic flexible aggregation step usable in the pipeline
"""
import collections
from typing import Callable, Generic, Iterable, Mapping, TypeVar, Union, Literal

from configmate.common import context, exceptions, registry, transformations, types

T = TypeVar("T")
U = TypeVar("U", bound="AggregationSpec")
V = TypeVar("V")


class Aggregator(transformations.Transformer[Iterable, T], Generic[T]):
    """An aggregator that can be used to validate ensure value."""

    input_type = Iterable  # type: ignore


AggregationSpec = Union[Callable[[Iterable], T], Literal["overlay"]]
AggregatorFactoryMethod = Callable[[U], Aggregator[T]]


###
# factory for validation strategies
###
class AggregatorFactory(
    registry.StrategyRegistryMixin[AggregationSpec[U], AggregatorFactoryMethod[U, T]],
    types.RegistryProtocol[AggregationSpec[U], Aggregator[T]],
):
    def __getitem__(self, key: AggregationSpec[V]) -> Aggregator[V]:
        return self.get_first_match(key)(key)  # type: ignore


###
# concrete validation steps
###
class FunctionAggregator(Aggregator[T]):
    def __init__(self, aggregator_function: Callable[[Iterable[T]], T]) -> None:
        super().__init__()
        self._method = aggregator_function

    def _apply(self, ctx: context.Context, input_: Iterable[T]) -> T:
        return self._method(input_)


class OverlayAggregator(Aggregator[Mapping]):
    output_type = Mapping

    def _apply(self, ctx: context.Context, input_: Iterable[Mapping]) -> Mapping:
        chainmap = self._make_chainmap(input_)
        chainmap.maps.reverse()  # last map has highest priority
        return chainmap

    def _make_chainmap(self, configs: Iterable) -> collections.ChainMap:
        try:
            return collections.ChainMap(*map(dict, configs))
        except TypeError as exc:
            raise exceptions.AggregationFailure(f"Can't aggregate {configs=}") from exc


###
# register strategies in order of priority
###
AggregatorFactory.register(callable, FunctionAggregator)
AggregatorFactory.register(lambda spec: spec == "overlay", OverlayAggregator)  # type: ignore
