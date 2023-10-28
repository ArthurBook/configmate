import fnmatch
import json
import configparser
import os
from typing import Any, Callable, Dict, Optional, Union
from xml.etree import ElementTree as etree

import toml
import yaml

from configmate import base
from configmate import interface as i


def infer_parser(path: Union[str, os.PathLike]) -> "Parser":
    return Parser(ParserRegistry.get_strategy(path))


class Parser(base.HasDescription):
    def __init__(self, parse_backend: Callable[[i.ConfigLike], Any]) -> None:
        self.parse_backend = parse_backend

    def __call__(self, text: i.ConfigLike) -> Any:
        return self.parse_backend(text)


class ParserRegistry(base.BaseRegistry[str, i.Transformer[i.ConfigLike, Any]]):
    @staticmethod
    def is_valid_strategy(type_: Any, key: str) -> bool:
        return fnmatch.fnmatch(type_, key)


### .INI
@ParserRegistry.register("*.ini", "*.INI")
def parse_ini(text: str) -> Any:
    (cnfparser := configparser.ConfigParser()).read_string(text)
    return convert_ini_to_dict(cnfparser)


def convert_ini_to_dict(cnfparser: configparser.ConfigParser) -> Dict[str, Dict]:
    return {section: dict(cnfparser[section]) for section in cnfparser.sections()}


### .JSON
@ParserRegistry.register("*.json", "*.JSON")
def parse_json(text: i.ConfigLike) -> Any:
    return json.loads(text)


### .XML
@ParserRegistry.register("*.xml", "*.XML")
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
@ParserRegistry.register("*.toml", "*.tml", "*.TOML", "*.TML")
def parse_toml(text: i.ConfigLike) -> Any:
    return toml.loads(text)


### .YAML
@ParserRegistry.register("*.yaml", "*.yml", "*.YAML", "*.YML")
def parse_yaml_safe(text: i.ConfigLike) -> Any:
    return yaml.safe_load(text)
