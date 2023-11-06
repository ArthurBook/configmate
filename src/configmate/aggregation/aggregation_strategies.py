import collections
import itertools
from typing import ChainMap, Collection, List, Mapping, Sequence, Set, TypeVar

from configmate import _utils, base
from configmate.aggregation import aggregator_factory

T = TypeVar("T")


@aggregator_factory.AggregatorFactoryRegistry.register(_utils.always, rank=-1)
class StrategyBasedAggregator(base.BaseAggregator):
    def aggregate(self, sequence: Sequence[T]) -> T:
        return AggregationStrategyRegistry.get_strategy(sequence)(sequence)


class AggregationStrategyRegistry(base.BaseMethodStore[Sequence[T], T]):
    """Registry for aggregation strategies."""


### Implementations
@AggregationStrategyRegistry.register(_utils.is_sequence_of_collections)
def aggregate_with_chain(items: Sequence[Collection]) -> List:
    return list(itertools.chain.from_iterable(items))


@AggregationStrategyRegistry.register(_utils.is_sequence_of_mappings)
def aggregate_with_chainmap(items: Sequence[Mapping]) -> ChainMap:
    config_chainmap = collections.ChainMap(*(dict(config) for config in items))
    config_chainmap.maps.reverse()
    return config_chainmap
