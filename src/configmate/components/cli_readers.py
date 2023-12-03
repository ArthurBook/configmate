import re
from typing import (
    Callable,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from configmate.base import constants, operators, types

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


###
# Filters for command line arguments
###
class CliSectionReader(operators.Operator[Collection[str], List[str]]):
    """Reads a section of command line arguments."""

    def __init__(
        self,
        section_start_token: Optional[str] = None,
        section_end_token: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    ) -> None:
        super().__init__()
        self.start_token = section_start_token
        self.end_token = section_end_token

    def _transform(self, ctx: operators.Context, input_: Collection[str]) -> List[str]:
        section = SectionTracker(self.start_token, self.end_token)
        return [arg for arg in input_ if arg in section]


class ArgSelector(operators.Operator[Sequence[str], List[str]]):
    """Filters out command line arguments using a callable."""

    def __init__(self, arg_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX) -> None:
        super().__init__()
        self._prefix = arg_prefix
        self._trigger = PrefixTrigger(self._prefix)

    def _transform(self, ctx: operators.Context, input_: Sequence[str]) -> List[str]:
        return [arg.lstrip(self._prefix) for arg in input_ if self._trigger(arg)]


class KeyValueSelector(operators.Operator[Sequence[str], List[Tuple[str, str]]]):
    """Filters out command line arguments using a callable."""

    def __init__(
        self, key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX
    ) -> None:
        super().__init__()
        self._prefix = key_prefix
        self._trigger = PrefixTrigger(key_prefix)

    def _transform(
        self, ctx: operators.Context, input_: Sequence[str]
    ) -> List[Tuple[str, str]]:
        pairs = zip(input_, input_[1:])
        return [(k.lstrip(self._prefix), v) for k, v in pairs if self._trigger(k)]


class DictParser(operators.Operator[Tuple[str, str], types.NestedDict[T_co]]):
    """Filters out command line arguments using a callable."""

    def __init__(
        self,
        key_split_delimiter=constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
        arg_parser: Callable[[str], T_co] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
    ) -> None:
        super().__init__()
        self._delimiter = key_split_delimiter
        self._parser = arg_parser

    def _transform(
        self, ctx: operators.Context, input_: Tuple[str, str]
    ) -> types.NestedDict[T_co]:
        key, value = input_
        return nest_in_dict(key.split(self._delimiter), self._parser(value))


###
# Helpers
###
def lstrip_prefix(prefix: str, string: str) -> str:
    """Removes the prefix from the string."""
    return string[len(prefix) :]


def nest_in_dict(key_sequence: Iterable[str], value: T) -> types.NestedDict[T]:
    """Make a nested dictionary from a sequence of keys and a value.

    E.g. nest_in_dict(["a", "b", "c"], 1) -> {"a": {"b": {"c": 1}}}
    """

    def nest_dict() -> Union[Dict, T]:
        key = next(key_iterator, types.SENTINEL)
        return {key: nest_dict()} if key != types.SENTINEL else value

    key_iterator = iter(key_sequence)
    return cast(types.NestedDict[T], nest_dict())


class SectionTracker:
    """Tracks whether a section has started and ended.

    A section starts when the first argument matches the start trigger.
    A section ends when the first argument matches the end trigger.
    """

    def __init__(self, start: Optional[str], end: Optional[str]) -> None:
        self._start_trigger = PrefixTrigger(start) if start else lambda _: True
        self._end_trigger = PrefixTrigger(end) if end else lambda _: False
        self._section_started = self._section_ended = False

    def __contains__(self, arg: str) -> bool:
        self._section_started |= self._start_trigger(arg)  # type: ignore
        self._section_ended |= self._end_trigger(arg)  # type: ignore
        return self._section_started and not self._section_ended


class PrefixTrigger:
    """A callable that returns True if the argument starts with the prefix."""

    def __init__(self, prefix: str) -> None:
        escaped_prefix = re.escape(prefix)
        self.pattern = re.compile(f"^{escaped_prefix}([^{escaped_prefix}]|$)")

    def __call__(self, arg: str) -> bool:
        return self.pattern.search(arg) is not None
