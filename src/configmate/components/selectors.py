""" Generic flexible aggregation step usable in the pipeline
"""

import functools

from typing import Any, Callable, NoReturn, Sequence, TypeVar, Union

from configmate.base import exceptions, operators, registry

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
SpecT_co = TypeVar("SpecT_co", bound="SectionSelectionSpec", covariant=True)


class SectionSelector(operators.Operator[T_contra, T_co]):
    """Selects a section from the config"""


SectionSelectionSpec = Union[Callable[[T_contra], T_co], str, Sequence[str]]
SectionSelectorFactoryMethod = Callable[[SpecT_co], SectionSelector[T_contra, T_co]]


###
# factory for validation strategies
###
class SectionSelectorFactory(
    registry.StrategyRegistryMixin[SectionSelectionSpec, SectionSelectorFactoryMethod]
):
    @classmethod
    def build_selector(
        cls, key: SectionSelectionSpec[T_contra, T_co]
    ) -> SectionSelector[T_contra, T_co]:
        return cls.get_first_match(key)(key)


###
# concrete validation steps
###
class FunctionSectionSelector(SectionSelector):
    def __init__(self, selector_function: Callable[[Any], Any]) -> None:
        super().__init__()
        self._method = selector_function

    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        return self._method(input_)


class KeySelector(SectionSelector):
    def __init__(self, section: Union[str, Sequence[str]]) -> None:
        super().__init__()
        self._section = (section,) if isinstance(section, str) else section

    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        try:
            return functools.reduce(lambda d, key: d[key], self._section, input_)
        except (TypeError, KeyError) as exc:
            self._raise_missing(input_, exc)

    def _raise_missing(self, input_: Any, exc: Exception) -> NoReturn:
        raise exceptions.SectionNotFound(f"{self._section=} not in {input_=}") from exc


###
# register strategies in order of priority
###
def is_sequence_or_string(spec: Any) -> bool:
    return isinstance(spec, (Sequence, str))


SectionSelectorFactory.register(callable, FunctionSectionSelector)
SectionSelectorFactory.register(is_sequence_or_string, KeySelector)
