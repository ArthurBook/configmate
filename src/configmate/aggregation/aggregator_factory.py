from typing import Callable, Optional, Sequence, TypeVar

from configmate import base

T = TypeVar("T")


class AggregatorFactoryRegistry(
    base.FactoryRegistry[Optional[Callable[[Sequence[T]], T]], base.BaseAggregator[T]]
):
    """Registry for aggregator factories."""
