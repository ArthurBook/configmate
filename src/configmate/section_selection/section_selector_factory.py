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
def construct_sectionselector(spec: Sequence[str]) -> base.BaseSectionSelector[_utils.RecursiveMapping]: ... # pylint: disable=line-too-long
@overload
def construct_sectionselector(spec: int) -> base.BaseSectionSelector[Sequence]: ...
@overload
def construct_sectionselector(spec: Sequence[int]) -> base.BaseSectionSelector[_utils.RecursiveSequence]: ... # pylint: disable=line-too-long
@overload
def construct_sectionselector(spec: Callable[[T], Any]) -> base.BaseSectionSelector[T]: ...
@overload
def construct_sectionselector(spec: base.BaseSectionSelector[T]) -> base.BaseSectionSelector[T]: ...
# fmt: on
def construct_sectionselector(spec: SectionSelectionSpec) -> base.BaseSectionSelector:
    return SectionSelectorFactoryRegistry.get_strategy(spec)(spec)


class SectionSelectorFactoryRegistry(
    base.BaseMethodStore[SectionSelectionSpec, base.BaseSectionSelector]
):
    """Registry for section selector factories."""


@SectionSelectorFactoryRegistry.register(_utils.check_if_none, rank=0)
class NoSectionSelector(base.BaseSectionSelector):
    def select(self, config: T) -> T:
        return config


## checks if the spec a string or a sequence of strings
def _check_if_str_or_sequence_of_str(spec: SectionSelectionSpec) -> bool:
    return isinstance(spec, str) or (
        isinstance(spec, Sequence) and all(isinstance(item, str) for item in spec)
    )


@SectionSelectorFactoryRegistry.register(_check_if_str_or_sequence_of_str, rank=1)
class KeyBasedSectionSelector(base.BaseSectionSelector[_utils.RecursiveMapping]):
    def __init__(self, section: Union[str, Sequence[str]]) -> None:
        self._section = (section,) if isinstance(section, str) else section

    def select(self, config: _utils.RecursiveMapping) -> Any:
        try:
            return _utils.get_nested(config, *self._section)
        except KeyError:
            self.get_not_found_exc(config, self._section)


## checks if the spec an int or a sequence of ints
def _check_if_int_or_sequence_of_int(spec: SectionSelectionSpec) -> bool:
    return isinstance(spec, int) or (
        isinstance(spec, Sequence) and all(isinstance(item, int) for item in spec)
    )


@SectionSelectorFactoryRegistry.register(_check_if_int_or_sequence_of_int, rank=2)
class IndexBasedSectionSelector(base.BaseSectionSelector[_utils.RecursiveSequence]):
    def __init__(self, section: Union[int, Sequence[int]]) -> None:
        self._section = (section,) if isinstance(section, int) else section

    def select(self, config: _utils.RecursiveSequence) -> Any:
        try:
            return _utils.get_nested(config, *self._section)
        except IndexError:
            self.get_not_found_exc(config, self._section)
