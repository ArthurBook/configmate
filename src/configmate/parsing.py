import fnmatch
import functools
import json
from configparser import ConfigParser
from typing import Any, Dict, Optional, Union
from xml.etree import ElementTree as etree

import toml
import yaml

from configmate import base, exceptions
from configmate import interface as i


def parse_with_inferred_parser(config_string: i.ConfigLike, path: i.FilePath) -> Any:
    return FileParserRegistry.from_path(path)(config_string)


class FileParserRegistry(base.BaseRegistry[str, i.Transformer[i.ConfigLike, Any]]):
    @classmethod
    def from_path(cls, path: i.FilePath) -> i.Transformer[i.ConfigLike, Any]:
        matcher = functools.partial(fnmatch.fnmatch, str(path))
        for _, parser in filter(lambda x: matcher(x[0]), cls.iterate_by_priority()):
            return parser
        raise exceptions.UnknownFileExtension(f"No parser for {path=}")


### .INI
@FileParserRegistry.register({"*.ini"})
def parse_ini(text: i.ConfigLike) -> Any:
    (configparser := ConfigParser()).read_string(text)
    return convert_to_ini_to_dict(configparser)


def convert_to_ini_to_dict(configparser: ConfigParser) -> Dict[str, Dict[str, str]]:
    return {section: dict(configparser[section]) for section in configparser.sections()}


### .JSON
@FileParserRegistry.register({"*.json"})
def parse_json(text: i.ConfigLike) -> Any:
    return json.loads(text)


### .XML
@FileParserRegistry.register({"*.xml"})
def parse_xml(text: i.ConfigLike) -> Any:
    root = etree.fromstring(text)
    return convert_etree_to_dict(root)


Tree = Dict[str, Optional[Union[str, "Tree"]]]


def convert_etree_to_dict(element: etree.Element) -> Optional[Union[str, Tree]]:
    if not (children := list(element)):
        return element.text
    return {
        child.tag: child.text if not list(child) else convert_etree_to_dict(child)
        for child in children
    }


### .TOML
@FileParserRegistry.register({"*.toml", "*.tml"})
def parse_toml(text: i.ConfigLike) -> Any:
    return toml.loads(text)


### .YAML
@FileParserRegistry.register({"*.yaml", "*.yml"})
def parse_yaml_safe(text: i.ConfigLike) -> Any:
    return yaml.safe_load(text)
