import os
from typing import Any, Callable, Literal, TypeVar, Union, overload

from configmate import _utils, base

T = TypeVar("T")
ParsingSpec = Union[
    Literal[None],
    Callable[[str], T],
    Union[str, os.PathLike],
    base.BaseParser[T],
]


# fmt: off
@overload
def construct_parser(spec: ParsingSpec) -> base.BaseParser:
    """
    Construct a parser by invoking the `ParserFactoryRegistry`.
    - If spec is a callable, returns a parser applying the callable for validation.
    - If spec is a path-like object, returns a parser matchin the file extension for instantiation.
    - If spec is an existing parser, returns the same parser.
    """
@overload
def construct_parser(spec: Callable[[Any], T]) -> base. BaseParser[T]: ...
@overload
def construct_parser(spec: Union[str, os.PathLike]) -> base.BaseParser: ...
@overload
def construct_parser(spec: base.BaseParser[T]) -> base.BaseParser[T]: ...
# fmt: on
def construct_parser(spec: ParsingSpec) -> base.BaseParser:
    return ParserFactoryRegistry.get_strategy(spec)(spec)


class ParserFactoryRegistry(base.BaseMethodStore[ParsingSpec, base.BaseParser]):
    ...


@ParserFactoryRegistry.register(_utils.check_if_callable, rank=1)
class FunctionalParser(base.BaseParser):
    def __init__(self, function_: Callable[[str], Any]) -> None:
        self._backend = function_

    def parse(self, configlike: str) -> Any:
        return self._backend(configlike)
