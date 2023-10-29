import os
from typing import Any, Callable, Literal, TypeVar, Union
from configmate import base, commons
from configmate.parsing import parsers

T = TypeVar("T", Literal[None], base.BaseParser, Union[str, os.PathLike])


class ParserFactoryRegistry(base.BaseFactoryRegistry[T, base.BaseParser]):
    ...


class ConstructedParser(base.BaseParser):
    def __init__(self, parse_backend: Callable[[str], Any]) -> None:
        self._backend = parse_backend

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)


@ParserFactoryRegistry.register(commons.check_if_none)
class NoParser(ConstructedParser):
    def parse(self, configlike: str) -> str:
        return configlike


@ParserFactoryRegistry.register(commons.make_typechecker(str, os.PathLike))
class FileNameInferredParser(base.BaseParser):
    def __init__(self, path: Union[str, os.PathLike]) -> None:
        self._path = path
        self._backend = parsers.ParserRegistry.get_strategy(path)

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)
