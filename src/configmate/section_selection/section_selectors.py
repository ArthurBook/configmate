from typing import Any, Sequence, Union

from configmate import _utils, base
from configmate.section_selection import section_selector_factory as factory


@factory.SelectorFactoryRegistry.register(_utils.is_string, rank=1)
@factory.SelectorFactoryRegistry.register(_utils.is_sequence_of_strings, rank=2)
class KeyBasedSectionSelector(base.BaseSectionSelector[base.RecursiveMapping]):
    def __init__(self, section: Union[str, Sequence[str]]) -> None:
        self._section = (section,) if isinstance(section, str) else section

    def select(self, config: base.RecursiveMapping) -> Any:
        try:
            return _utils.get_nested(config, *self._section)
        except KeyError:
            self.get_not_found_exc(config, self._section)


@factory.SelectorFactoryRegistry.register(_utils.is_integer, rank=3)
@factory.SelectorFactoryRegistry.register(_utils.is_sequence_of_strings, rank=4)
class IndexBasedSectionSelector(base.BaseSectionSelector[base.RecursiveSequence]):
    def __init__(self, section: Union[int, Sequence[int]]) -> None:
        self._section = (section,) if isinstance(section, int) else section

    def select(self, config: base.RecursiveSequence) -> Any:
        try:
            return _utils.get_nested(config, *self._section)
        except IndexError:
            self.get_not_found_exc(config, self._section)
