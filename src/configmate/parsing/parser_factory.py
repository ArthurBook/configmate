import os
from typing import Any, Callable, Literal, Union

from configmate import base, commons
from configmate.parsing import parsers

ParsingSpec = Union[Literal[None], base.BaseParser, Union[str, os.PathLike]]


class ParserFactoryRegistry(base.FactoryRegistry[ParsingSpec, base.BaseParser]):
    ...


@ParserFactoryRegistry.register(commons.check_if_none)
class NoParser(base.BaseParser):
    def __init__(self, _: Literal[None]) -> None:
        super().__init__()

    def parse(self, configlike: str) -> str:
        return configlike


@ParserFactoryRegistry.register(commons.check_if_callable)
class FunctionalParser(base.BaseParser):
    def __init__(self, function_: Callable[[str], Any]) -> None:
        self._backend = function_

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)


@ParserFactoryRegistry.register(commons.make_typechecker(str, os.PathLike))
class FileNameInferredParser(base.BaseParser):
    def __init__(self, path: Union[str, os.PathLike]) -> None:
        self._path = path
        self._backend = parsers.ParserRegistry.get_strategy(path)

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)
