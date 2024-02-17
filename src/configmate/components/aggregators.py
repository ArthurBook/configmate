""" Generic flexible aggregation step usable in the pipeline
"""

import collections
import itertools
from typing import Any, Callable, Iterable, List, Mapping, Sequence, TypeVar, Union

from configmate.base import exceptions, operators, registry

T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

AggregationSpec = Union[Callable[[Iterable[T_contra]], T_co], Any]
_SpecT_co = TypeVar("_SpecT_co", bound=AggregationSpec, covariant=True)
AggregatorFactoryMethod = Callable[[_SpecT_co], "Aggregator"]


###
# base class for aggregation steps
###
class Aggregator(operators.Operator[Iterable[T_contra], T_co]):
    """An aggregator that can be used to validate ensure value."""

    input_type = Iterable  # type: ignore


###
# factory for validation strategies
###
class AggregatorFactory(
    registry.StrategyRegistryMixin[AggregationSpec, AggregatorFactoryMethod],
):
    @classmethod
    def build_aggregator(cls, key: AggregationSpec[T, U]) -> Aggregator[T, U]:
        return cls.get_first_match(key)(key)


###
# concrete validation steps
###
class FunctionAggregator(Aggregator[T_contra, T_co]):
    def __init__(
        self, aggregator_function: Callable[[Iterable[T_contra]], T_co]
    ) -> None:
        super().__init__()
        self._method = aggregator_function

    def _transform(self, ctx: operators.Context, input_: Iterable[T_contra]) -> T_co:
        return self._method(input_)


class InferredAggregator(Aggregator[T, T]):
    def _transform(self, ctx: operators.Context, input_: Iterable[T]) -> T:
        if len(input_ := list(input_)) == 1:
            return input_[0]
        if all(isinstance(x, Sequence) for x in input_):
            return self._aggregate_sequences(input_)  # type: ignore
        if all(isinstance(x, Mapping) for x in input_):
            return self._aggregate_mappings(input_)  # type: ignore
        raise exceptions.AggregationFailure(f"Can't aggregate mixed types {input_=}")

    def _aggregate_sequences(self, sequences: Iterable[Sequence]) -> List:
        return list(itertools.chain.from_iterable(sequences))

    def _aggregate_mappings(self, configs: Iterable[Mapping]) -> Mapping:
        try:
            configs = list(configs)
            chainmap = collections.ChainMap(*map(dict, configs))
        except (ValueError, TypeError) as exc:
            raise exceptions.AggregationFailure(f"Can't aggregate {configs=}") from exc
        chainmap.maps.reverse()  # last map has highest priority
        return dict(chainmap)


###
# register strategies in order of priority
###
def always(_: AggregationSpec) -> bool:
    return True


AggregatorFactory.register(callable, FunctionAggregator)
AggregatorFactory.register(always, InferredAggregator)
