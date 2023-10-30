import collections
import itertools
from typing import Callable, ChainMap, Collection, List, Mapping, Sequence, Set, TypeVar

from configmate import base, commons
from configmate.aggregation import aggregator_factory

T = TypeVar("T")


@aggregator_factory.AggregatorFactoryRegistry.register(commons.always)
class StrategyBasedAggregator(base.BaseAggregator[T]):
    def aggregate(self, sequence: Sequence[T]) -> T:
        aggregator_cls = AggregationStrategyRegistry.get_strategy(sequence)
        return aggregator_cls(sequence)


class AggregationStrategyRegistry(
    base.BaseRegistry[Sequence[T], Callable[[Sequence[T]], T]]
):
    """Registry for aggregation strategies."""


### Implementations
@AggregationStrategyRegistry.register(commons.make_typechecker(Sequence, Set))
def aggregate_with_chain(items: Sequence[Collection]) -> List:
    return list(itertools.chain.from_iterable(items))


@AggregationStrategyRegistry.register(commons.make_typechecker(Mapping))
def aggregate_with_chainmap(items: Sequence[Mapping]) -> ChainMap:
    config_chainmap = collections.ChainMap(*(dict(config) for config in items))
    config_chainmap.maps.reverse()
    return config_chainmap
