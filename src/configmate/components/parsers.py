""" Parsing steps for the pipeline
"""

import configparser
import dataclasses
import json
import os
import pathlib
from typing import Any, Callable, Dict, Generic, Literal, Type, TypeVar, Union
from xml.etree import ElementTree as etree

from configmate.base import operators, registry, types

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
SpecT_co = TypeVar("SpecT_co", bound="ParsingSpec", covariant=True)


###
# Parser base class
###
class Parser(operators.Operator[Any, T_co], Generic[T_co]): ...


@dataclasses.dataclass
class InferFrom(Generic[T_co]):
    source_operator: T_co


ParsingSpec = Union[
    Callable[[str], T_co],
    Union[str, os.PathLike],
    InferFrom[operators.Operator[Any, types.FilePath]],
]
ParserFactoryMethod = Callable[[SpecT_co], Parser[T_co]]


###
# factory for parser strategies
###
class ParserFactory(registry.StrategyRegistryMixin[ParsingSpec, ParserFactoryMethod]):
    @classmethod
    def infer_from(cls, step: operators.Operator[Any, types.FilePath]) -> Parser[Any]:
        return cls.build_parser(InferFrom(step))

    @classmethod
    def build_parser(cls, key: ParsingSpec[T]) -> Parser[T]:
        return cls.get_first_match(key)(key)


###
# factory for file format parser strategies
###
class FileFormatParserRegistry(registry.DictRegistryMixin[str, Type[Parser[Any]]]):
    @classmethod
    def infer_parser(cls, path_or_extension: types.FilePath) -> Parser[Any]:
        if suffix := pathlib.Path(path_or_extension).suffix:
            return cls.lookup(suffix)()
        return cls.lookup(cls._normalize_extension(path_or_extension))()

    @classmethod
    def add_strategy(cls, strategy: Type[Parser[Any]], *extensions: str) -> None:
        for extension in extensions:
            cls.register(cls._normalize_extension(extension), strategy)

    @staticmethod
    def _normalize_extension(extension: Union[str, os.PathLike]) -> str:
        return f".{str(extension).lstrip('.')}"


###
# concrete parsers
###
class FunctionParser(Parser[T_co]):
    def __init__(self, parser: Callable[[str], T_co]) -> None:
        super().__init__()
        self._parser = parser

    def _transform(self, ctx: operators.Context, input_: Any) -> T_co:
        return self._parser(input_)


class InferredParser(Parser[Any]):
    """A parser that infers the file format from the file extension."""

    infer_parser = staticmethod(FileFormatParserRegistry.infer_parser)

    def __init__(
        self, infer_via: InferFrom[operators.Operator[Any, types.FilePath]]
    ) -> None:
        super().__init__()
        self._path_sender = infer_via.source_operator
        infer_via.source_operator.append_callback(self._store_path)

    def _transform(self, ctx: operators.Context, input_: str) -> Any:
        filename: types.FilePath = ctx[self._path_sender].filepath
        compatible_parser = self.infer_parser(filename)
        return compatible_parser(input_)

    def _store_path(self, ctx: operators.Context, result: types.FilePath) -> None:
        ctx[self._path_sender].filepath = result


###
# File format specific parsers
###
class JsonParser(Parser[Any]):
    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        return json.loads(input_)


class IniParser(Parser[Any]):
    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        (cnfparser := configparser.ConfigParser()).read_string(input_)
        return self._convert_ini_to_dict(cnfparser)

    @staticmethod
    def _convert_ini_to_dict(cnfparser: configparser.ConfigParser) -> Dict[str, Dict]:
        return {section: dict(cnfparser[section]) for section in cnfparser.sections()}


class XmlParser(Parser[Any]):
    XmlTree = Union[Literal[None], str, Dict[str, "XmlTree"]]

    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        root = etree.fromstring(input_)
        return self._convert_etree_to_dict(root)

    @staticmethod
    def _convert_etree_to_dict(element: etree.Element) -> XmlTree:
        if not (children := list(element)):
            return element.text
        return {
            child.tag: (
                child.text
                if not list(child)
                else XmlParser._convert_etree_to_dict(child)
            )
            for child in children
        }


###
# register default strategies
###
FileFormatParserRegistry.add_strategy(JsonParser, ".json", ".JSON")
FileFormatParserRegistry.add_strategy(IniParser, ".ini", ".INI")
FileFormatParserRegistry.add_strategy(XmlParser, ".xml", ".XML")


def is_inferred_from(spec: ParsingSpec) -> bool:
    return isinstance(spec, InferFrom)


def is_string(spec: ParsingSpec) -> bool:
    return isinstance(spec, str)


ParserFactory.register(is_inferred_from, InferredParser)
ParserFactory.register(callable, FunctionParser)
ParserFactory.register(is_string, FileFormatParserRegistry.infer_parser)
