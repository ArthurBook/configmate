from typing import Any, Callable, Literal, Mapping, Sequence, TypeVar, Union, overload

from configmate import _utils, base

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


# fmt: off
@overload
def construct_sectionselector(spec: Literal[None]) -> base.BaseSectionSelector[Any]: ...
@overload
def construct_sectionselector(spec: str) -> base.BaseSectionSelector[Mapping[str,Any]]: ...
@overload
def construct_sectionselector(spec: Sequence[str]) -> base.BaseSectionSelector[base.RecursiveMapping]: ... # pylint: disable=line-too-long
@overload
def construct_sectionselector(spec: int) -> base.BaseSectionSelector[Sequence]: ...
@overload
def construct_sectionselector(spec: Sequence[int]) -> base.BaseSectionSelector[base.RecursiveSequence]: ... # pylint: disable=line-too-long
@overload
def construct_sectionselector(spec: Callable[[T], Any]) -> base.BaseSectionSelector[T]: ...
@overload
def construct_sectionselector(spec: base.BaseSectionSelector[T]) -> base.BaseSectionSelector[T]: ...
# fmt: on
def construct_sectionselector(spec: SectionSelectionSpec) -> base.BaseSectionSelector:
    return SelectorFactoryRegistry.get_strategy(spec)(spec)


class SelectorFactoryRegistry(
    base.BaseMethodStore[SectionSelectionSpec, base.BaseSectionSelector]
):
    """Registry for section selector factories."""


@SelectorFactoryRegistry.register(_utils.check_if_none, rank=0)
class NoSectionSelector(base.BaseSectionSelector):
    def select(self, config: T) -> T:
        return config
