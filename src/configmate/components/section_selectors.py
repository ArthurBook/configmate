""" Generic flexible aggregation step usable in the pipeline
"""
import functools
from typing import Any, Callable, NoReturn, Sequence, TypeVar, Union

from configmate.common import context, exceptions, registry, transformations, types

T = TypeVar("T")
U = TypeVar("U", bound="SectionSelectionSpec")
V = TypeVar("V")


class SectionSelector(transformations.Transformer[Any, Any]):
    """Selects a section from the config"""


SectionSelectionSpec = Union[Callable[[Any], Any], str, Sequence[str]]
SectionSelectorFactoryMethod = Callable[[U], SectionSelector]


###
# factory for validation strategies
###
class SectionSelectorFactory(
    registry.StrategyRegistryMixin[SectionSelectionSpec, SectionSelectorFactoryMethod],
    types.RegistryProtocol[SectionSelectionSpec, SectionSelector],
):
    def __getitem__(self, key: SectionSelectionSpec) -> SectionSelector:
        return self.get_first_match(key)(key)


###
# concrete validation steps
###
class FunctionSectionSelector(SectionSelector):
    def __init__(self, selector_function: Callable[[Any], Any]) -> None:
        super().__init__()
        self._method = selector_function

    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        return self._method(input_)


class KeySelector(SectionSelector):
    def __init__(self, section: Union[str, Sequence[str]]) -> None:
        super().__init__()
        self._section = (section,) if isinstance(section, str) else section

    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        try:
            return functools.reduce(lambda d, key: d[key], self._section, input_)
        except (TypeError, KeyError) as exc:
            self._raise_missing(input_, exc)

    def _raise_missing(self, input_: Any, exc: Exception) -> NoReturn:
        raise exceptions.SectionNotFound(f"{self._section=} not in {input_=}") from exc


###
# register strategies in order of priority
###
# fmt: off
SectionSelectorFactory.register(callable, FunctionSectionSelector)
SectionSelectorFactory.register(lambda spec: isinstance(spec, (Sequence, str)), KeySelector)
# fmt: on
