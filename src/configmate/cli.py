import abc
import re
import sys
from typing import Generator, Iterable, Iterator

from typing_extensions import Self

from configmate import interface

DEFAULT_SECTION_END_PATTERN = re.compile(r"^\/$")


class CliSectionSyntax(interface.Source[Iterator[str]]):
    def __iter__(self) -> Iterator[str]:
        section_tracker = self.in_section()
        next(section_tracker)  # prime
        return filter(section_tracker.send, sys.argv)

    @abc.abstractmethod
    def is_start_of_section(self, arg: str) -> bool:
        ...

    @abc.abstractmethod
    def is_end_of_section(self, arg: str) -> bool:
        ...

    def in_section(self, _arg: str = "") -> Generator[bool, str, None]:
        while not self.is_start_of_section(_arg):
            _arg = yield False
        while not self.is_end_of_section(_arg):
            _arg = yield True

    def read(self) -> Iterator[str]:
        return iter(self)


class CliSectionRegexSyntax(CliSectionSyntax):
    def __init__(self, start_pattern: re.Pattern, end_pattern: re.Pattern) -> None:
        super().__init__()
        self.start_regex = start_pattern
        self.end_regex = end_pattern

    def is_start_of_section(self, arg: str) -> bool:
        return self.start_regex.search(arg) is not None

    def is_end_of_section(self, arg: str) -> bool:
        return self.end_regex.search(arg) is not None

    @classmethod
    def default(cls, name: str, end: re.Pattern = DEFAULT_SECTION_END_PATTERN) -> Self:
        section_pattern = re.compile(f"^{name}")
        return cls(section_pattern, end)

    @classmethod
    def from_regex_strings(cls, start_regex: str, end_regex: str) -> Self:
        return cls(re.compile(start_regex), re.compile(end_regex))


class CliParser(abc.ABC, interface.ConfigReader[Iterable[str], interface.T_co]):
    @abc.abstractmethod
    def select(self, args: Iterable[str]) -> Iterable[Iterable[str]]:
        ...

    @abc.abstractmethod
    def parse(self, items: Iterable[str]) -> interface.T_co:
        ...

    def read_config(
        self, source: interface.Source[Iterable[str]]
    ) -> Iterator[interface.T_co]:
        return map(self.parse, self.select(source.read()))
