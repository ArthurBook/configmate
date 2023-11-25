""" Parsing steps for the pipeline
"""
import configparser
import json
import pathlib
from typing import Any, Callable, Dict, Generic, Literal, Type, TypeVar, Union
from xml.etree import ElementTree as etree

import toml
import yaml

from configmate.common import context, registry, transformations, types

T = TypeVar("T")
U = TypeVar("U", bound="ParsingSpec")
V = TypeVar("V")


###
# Parser base class
###
class Parser(transformations.Transformer[Any, T], Generic[T]):
    ...


ParsingSpec = Union[Callable[[str], T], types.FilePath]
ParserFactoryMethod = Callable[[U], Parser[T]]


###
# factory for parser strategies
###
class ParserFactory(
    registry.StrategyRegistryMixin[ParsingSpec[T], ParserFactoryMethod[U, T]],
    types.RegistryProtocol[ParsingSpec, Parser[T]],
):
    def __getitem__(self, key: ParsingSpec[V]) -> Parser[V]:
        return self.get_first_match(key)(key)  # type: ignore

    @classmethod
    def infer_from(
        cls, step: transformations.Transformer[Any, types.FilePath]
    ) -> "InferredParser":
        return InferredParser(step)


###
# factory for file format parser strategies
###
class FileFormatParserRegistry(
    registry.DictRegistryMixin[types.FilePath, Type[Parser[Any]]],
    types.RegistryProtocol[types.FilePath, Parser[Any]],
):
    def __getitem__(self, key: types.FilePath) -> Parser[Any]:
        return self.get_parser(key)

    @classmethod
    def get_parser(cls, path_or_extension: types.FilePath) -> Parser[Any]:
        if suffix := pathlib.Path(path_or_extension).suffix:
            return cls.lookup(suffix)()
        return cls.lookup(cls._normalize_extension(path_or_extension))()

    @classmethod
    def add_strategy(cls, strategy: Type[Parser[Any]], *extensions: str) -> None:
        for extension in extensions:
            cls.register(cls._normalize_extension(extension), strategy)

    @staticmethod
    def _normalize_extension(extension: types.FilePath) -> str:
        return f".{str(extension).lstrip('.')}"


class InferredParser(transformations.Transformer[str, Any]):
    """A parser that infers the file format from the file extension."""

    registry = FileFormatParserRegistry()
    CONTEXT_FILENAME_KEY = "_filepath"

    def __init__(
        self, infer_via: transformations.Transformer[Any, types.FilePath]
    ) -> None:
        super().__init__()
        infer_via.append_callback(self._set_path_in_context)

    def _apply(self, ctx: context.Context, input_: str) -> Any:
        filename = self._get_path_from_context(ctx)
        compatible_parser = self.registry[filename]
        return compatible_parser(input_)

    @staticmethod
    def _get_path_from_context(ctx: context.Context) -> types.FilePath:
        return ctx[InferredParser.CONTEXT_FILENAME_KEY]

    @staticmethod
    def _set_path_in_context(ctx: context.Context, result: types.FilePath) -> None:
        ctx[InferredParser.CONTEXT_FILENAME_KEY] = result


###
# concrete parsers
###
class FunctionParser(Parser[T]):
    def __init__(self, parser: Callable[[str], T]) -> None:
        super().__init__()
        self._parser = parser

    def _apply(self, ctx: context.Context, input_: Any) -> T:
        return self._parser(input_)


###
# File format specific parsers
###
class JsonParser(Parser[T]):
    def _apply(self, ctx: context.Context, input_: Any) -> T:
        return json.loads(input_)


class IniParser(Parser[Any]):
    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        (cnfparser := configparser.ConfigParser()).read_string(input_)
        return self._convert_ini_to_dict(cnfparser)

    @staticmethod
    def _convert_ini_to_dict(cnfparser: configparser.ConfigParser) -> Dict[str, Dict]:
        return {section: dict(cnfparser[section]) for section in cnfparser.sections()}


class XmlParser(Parser[Any]):
    XmlTree = Union[Literal[None], str, Dict[str, "XmlTree"]]

    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        root = etree.fromstring(input_)
        return self._convert_etree_to_dict(root)

    @staticmethod
    def _convert_etree_to_dict(element: etree.Element) -> XmlTree:
        if not (children := list(element)):
            return element.text
        return {
            child.tag: child.text
            if not list(child)
            else XmlParser._convert_etree_to_dict(child)
            for child in children
        }


class YamlParser(Parser[Any]):
    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        return yaml.safe_load(input_)


class TomlParser(Parser[Any]):
    def _apply(self, ctx: context.Context, input_: Any) -> Any:
        return toml.loads(input_)


###
# register default strategies
###
# fmt: off
FileFormatParserRegistry.add_strategy(JsonParser, ".json", ".JSON")
FileFormatParserRegistry.add_strategy(IniParser, ".ini", ".INI")
FileFormatParserRegistry.add_strategy(XmlParser, ".xml", ".XML")
FileFormatParserRegistry.add_strategy(TomlParser, ".toml", ".TOML")
FileFormatParserRegistry.add_strategy(YamlParser, ".yaml", ".YAML")

ParserFactory.register(callable, FunctionParser)
ParserFactory.register(lambda spec: isinstance(spec, str), FileFormatParserRegistry.get_parser)
# fmt: on
