import abc
from typing import Any, Generic, Mapping, Sequence, TypeVar

AggInput = TypeVar("AggInput")
AggOutput = TypeVar("AggOutput")


class BaseAggregator(abc.ABC, Generic[AggInput, AggOutput]):
    """
    Aggregates one or more items of type AggInput into a single item of type AggOutput.
    When aggregating multiple items, the later items take precedence over the earlier items.
    If the aggregation is not possible, an exception is raised.
    """

    @abc.abstractmethod
    def aggregate(self, *items: AggInput) -> AggOutput:
        ...


class MapAggregator(BaseAggregator[Mapping[str, Any], Mapping[str, Any]], abc.ABC):
    ...


class SequenceAggregator(BaseAggregator[Sequence[Any], Sequence[Any]], abc.ABC):
    ...
