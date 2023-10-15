import abc
import functools
import re
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from typing_extensions import Annotated, Self

from configmate import interface as i, parsing_backends


### Defaults
DEFAULT_OVERRIDE_REGEX = "+"  # for example, "+foo.bar value"
DEFAULT_OVERLAY_REGEX = "++"  # for example, "++/path/to/file"
DEFAULT_END_SECTION_TOKEN = "/"  # for example, Raxban +i 1 ++ping/pong / Haxban ..."
ANY_SECTION = re.compile(".*")  # say True to all sections
DEFAULT_END = re.compile(rf"^{re.escape(DEFAULT_END_SECTION_TOKEN)}$")


class CliSectionFinder(i.Source[i.CliArgArray]):
    def __init__(self, start_pattern: re.Pattern, end_pattern: re.Pattern) -> None:
        super().__init__()
        self.start_regex = start_pattern
        self.end_regex = end_pattern

    def __iter__(self) -> Iterator[i.CliArg]:
        section_tracker = self.in_section()
        next(section_tracker)  # prime
        return filter(section_tracker.send, sys.argv)

    def read(self) -> i.CliArgArray:
        return iter(self)

    def in_section(self, _arg: i.CliArg = "") -> Generator[bool, str, None]:
        while self.start_regex.search(_arg) is None:
            _arg = yield False
        while self.end_regex.search(_arg) is None:
            _arg = yield True

    @classmethod
    def default(cls, name: Optional[str] = None, end: re.Pattern = DEFAULT_END) -> Self:
        section_pattern = re.compile(f"^{name}") if name else ANY_SECTION
        return cls(section_pattern, end)


### CliParser selects and parses config items from the command line
class CliOverrideParser(i.ConfigReader[i.CliArgArray, Iterator[Dict[str, Any]]]):
    def __init__(
        self,
        key_recognizer: Callable[[i.CliArg], bool],
        key_parser: Callable[[i.CliArg], Iterable[str]],
        value_parser: Callable[[i.ConfigLike], Any],
    ) -> None:
        super().__init__()
        self.key_recognizer = key_recognizer
        self.key_tokenizer = key_parser
        self.value_parser = value_parser

    def read_config(self, source: Iterable[i.CliArg]) -> Iterator[Dict[str, Any]]:
        for key_maybe, val_maybe in zip(args := list(source), args[1:]):
            if self.key_recognizer(key_maybe):
                yield self.parse_to_dict(key_maybe, self.parse_value(val_maybe))

    def parse_to_dict(self, key: i.CliArg, value: Any) -> Dict[str, Any]:
        override_loc = self.key_tokenizer(key)
        *next_val, first_dict = [value] + [{} for _ in override_loc]

        def make_dict(_dict: dict, _next_key: str) -> Union[Dict, Any]:
            next_dict = _dict[_next_key] = next_val.pop()
            return next_dict

        functools.reduce(make_dict, override_loc, first_dict)
        return first_dict

    def parse_value(self, value: Annotated[i.CliArg, i.ConfigLike]) -> Any:
        return self.value_parser(i.ConfigLike(value))

    @classmethod
    def from_tokens(cls, key_prefix: str, key_split_token: str) -> Self:
        key_pattern = compile_prefix_regex(key_prefix)

        def key_recognizer(arg: i.CliArg) -> bool:
            return key_pattern.search(arg) is not None

        def key_lexer(arg: i.CliArg) -> List[str]:
            parsed_arg = arg[len(key_prefix) :]
            return parsed_arg.split(key_split_token)

        value_parser = parsing_backends.JsonParser().parse
        return cls(key_recognizer, key_lexer, value_parser)

    
class CliOverlayParser(i.ConfigReader[i.CliArgArray, Iterator[i.PathLikeString]]):
    def __init__(
        self,
        selector: Callable[[i.CliArg], Union[i.HasBool, Any]],
        parser: Callable[[i.CliArg], i.PathLikeString],
    ) -> None:
        super().__init__()
        self.selector = selector
        self.parser = parser

    def read_config(self, source: i.CliArgArray) -> Iterator[i.PathLikeString]:
        yield from map(self.parser, filter(self.selector, source))

    @classmethod
    def from_prefix(cls, prefix: str = DEFAULT_OVERLAY_REGEX) -> Self:
        select_pattern = compile_prefix_regex(prefix)

        def selector(arg: i.CliArg) -> bool:
            return select_pattern.search(arg) is not None

        def parser(items: i.CliArg) -> i.PathLikeString:
            return items[len(prefix) :]

        return cls(selector, parser)


def compile_prefix_regex(prefix: str) -> re.Pattern:
    escaped_prefix = re.escape(prefix)
    return re.compile(f"^{escaped_prefix}[^{escaped_prefix}]")

