from typing import Any, Callable, Literal, Sequence, TypeVar, Union

from configmate import base

T = TypeVar("T")
SectionSelectionSpec = Union[
    Literal[None],
    str,
    Sequence[str],
    int,
    Sequence[int],
    Callable[[T], Any],
    base.BaseSectionSelector[T],
]


def make_sectionselector(spec: SectionSelectionSpec[T]) -> base.BaseSectionSelector[T]:
    return SelectorFactoryRegistry.get_strategy(spec)(spec)


class SelectorFactoryRegistry(
    base.BaseMethodStore[SectionSelectionSpec, base.BaseSectionSelector]
):
    """Registry for section selector factories."""
