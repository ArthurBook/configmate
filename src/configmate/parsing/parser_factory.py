import os
from typing import Any, Callable, Literal, TypeVar, Union

from configmate import base, config_sources

T = TypeVar("T")

ParsingSpec = Union[
    Literal[None],
    Callable[[str], T],
    Union[str, os.PathLike],
    config_sources.File,
    base.BaseParser[T],
]


def make_parser(spec: ParsingSpec[T]) -> base.BaseParser[T]:
    return ParserFactoryRegistry.get_strategy(spec)(spec)


class ParserFactoryRegistry(base.BaseMethodStore[ParsingSpec, base.BaseParser]):
    ...


@ParserFactoryRegistry.register(callable, rank=1)
class FunctionalParser(base.BaseParser):
    def __init__(self, function_: Callable[[str], Any]) -> None:
        self._backend = function_

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)
