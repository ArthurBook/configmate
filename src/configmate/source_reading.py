import dataclasses
import json
import pathlib
import re
import sys
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Tuple

from typing_extensions import Annotated, Self

from configmate import interface as i

### Defaults
DEFAULT_FILE_ENCODING = "utf-8"
DEFAULT_OVERRIDE_PREFIX = "+"  # for example: "+foo.bar value"
DEFAULT_OVERRIDE_KEY_SPLIT_TOKEN = "."  # splits +foo.bar to (foo, bar)
DEFAULT_OVERRIDE_VAL_PARSER = json.loads  # JSON
DEFAULT_OVERLAY_PREFIX = "++"  # for example: "++/path/to/file"
DEFAULT_SECTION_END_TOKEN = "/"  # for example: Raxban +i 1 ++ping/pong / Haxban ..."


### File reading from disk
@dataclasses.dataclass
class FileSource:
    path: i.FilePath
    encoding: str = DEFAULT_FILE_ENCODING

    def read(self) -> i.ConfigLike:
        return pathlib.Path(self.path).read_text(self.encoding)


class SectionFinder:
    def __init__(
        self,
        section_start_finder: Callable[[i.CliArg], bool],
        section_end_finder: Callable[[i.CliArg], bool],
    ) -> None:
        super().__init__()
        self.section_start_finder = section_start_finder
        self.section_end_finder = section_end_finder

    def __iter__(self) -> Iterator[i.CliArg]:
        section_tracker = self.in_section()
        next(section_tracker)  # prime
        return filter(section_tracker.send, sys.argv)

    def in_section(self, _arg: str = "") -> Generator[bool, str, None]:
        while not self.section_start_finder(_arg):
            _arg = yield False
        while not self.section_end_finder(_arg):
            _arg = yield True
        yield True  # for the last item

    @classmethod
    def from_tokens(cls, start: str, end: str = DEFAULT_SECTION_END_TOKEN) -> Self:
        start_pattern = RegexEvaluator.compile(rf"^{re.escape(start)}")
        end_pattern = RegexEvaluator.compile(rf"^{re.escape(end)}$")
        return cls(start_pattern, end_pattern)


class OverrideParser:
    def __init__(
        self,
        pair_selector: Callable[[Tuple[i.CliArg, i.CliArg]], bool],
        key_parser: Callable[[i.CliArg], Iterable[str]],
        value_parser: Callable[[Annotated[i.CliArg, i.ConfigLike]], Any],
    ) -> None:
        super().__init__()
        self.selector = pair_selector
        self.key_parser = key_parser
        self.val_parser = value_parser

    def parse(self, source: i.CliArgArray) -> Iterator[Dict[str, Any]]:
        for key, val in filter(self.selector, zip(args := list(source), args[1:])):
            yield make_nested_dict(self.key_parser(key), self.val_parser(val))

    @classmethod
    def from_tokens(
        cls,
        key_prefix: str = DEFAULT_OVERRIDE_PREFIX,
        key_split_token: str = DEFAULT_OVERRIDE_KEY_SPLIT_TOKEN,
        value_parser: Callable[[i.ConfigLike], Any] = DEFAULT_OVERRIDE_VAL_PARSER,
    ) -> Self:
        key_recognizer = RegexEvaluator.compile_from_prefix(key_prefix)

        def pair_finder(key_val_maybe: Tuple[i.CliArg, i.CliArg]) -> bool:
            return key_recognizer(key_val_maybe[0])

        def key_lexer(arg: i.CliArg) -> List[str]:
            return arg[len(key_prefix) :].split(key_split_token)

        return cls(pair_finder, key_lexer, value_parser)


def make_nested_dict(keys: Iterable[str], value: Any) -> Dict[str, Any]:
    def nest_dicts(_dict: Dict[str, Any], keys: Iterator[str]) -> Dict[str, Any]:
        if (_next_key := next(keys, None)) is not None:
            _dict[_next_key] = nest_dicts({}, keys)
        else:
            _dict[last_key] = value
        return _dict

    *_keys, last_key = keys
    nest_dicts(nested_dict := {}, iter(_keys))  # type: ignore
    return nested_dict


class OverlayParser:
    def __init__(
        self,
        selector: Callable[[i.CliArg], bool],
        parser: Callable[[i.CliArg], i.FilePath],
    ) -> None:
        super().__init__()
        self.selector = selector
        self.parser = parser

    def parse(self, source: i.CliArgArray) -> Iterator[i.FilePath]:
        yield from map(self.parser, filter(self.selector, source))

    @classmethod
    def from_prefix_token(cls, prefix: str = DEFAULT_OVERLAY_PREFIX) -> "OverlayParser":
        selector = RegexEvaluator.compile_from_prefix(prefix)

        def parser(items: i.CliArg) -> i.FilePath:
            return items[len(prefix) :]

        return OverlayParser(selector, parser)


@dataclasses.dataclass
class RegexEvaluator:
    __slots__ = ("pattern",)
    pattern: re.Pattern

    def __call__(self, arg: i.CliArg) -> bool:
        return self.pattern.search(arg) is not None  # pylint: disable=no-member

    @classmethod
    def compile_from_prefix(cls, prefix_pattern: str) -> "RegexEvaluator":
        escaped_prefix = re.escape(prefix_pattern)
        return cls.compile(f"^{escaped_prefix}[^{escaped_prefix}]")

    @classmethod
    def compile(cls, pattern: str) -> "RegexEvaluator":
        return RegexEvaluator(re.compile(pattern))
