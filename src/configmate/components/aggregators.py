""" Generic flexible aggregation step usable in the pipeline
"""

import collections
from typing import Callable, Dict, Iterable, Literal, Mapping, TypeVar, Union

from configmate.base import exceptions, operators, registry

T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

AggregationSpec = Union[Callable[[Iterable[T_contra]], T_co], Literal["overlay"]]
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


class OverlayAggregator(Aggregator[Mapping, Dict]):
    output_type = Dict

    def _transform(self, ctx: operators.Context, input_: Iterable[Mapping]) -> Dict:
        chainmap = self._make_chainmap(input_)
        chainmap.maps.reverse()  # last map has highest priority
        return dict(chainmap)

    def _make_chainmap(self, configs: Iterable) -> collections.ChainMap:
        try:
            configs = list(configs)
            return collections.ChainMap(*map(dict, configs))
        except (ValueError, TypeError) as exc:
            raise exceptions.AggregationFailure(f"Can't aggregate {configs=}") from exc


###
# register strategies in order of priority
###
AggregatorFactory.register(callable, FunctionAggregator)
AggregatorFactory.register(lambda spec: spec == "overlay", OverlayAggregator)
