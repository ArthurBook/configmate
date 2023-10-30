import configparser
import fnmatch
import json
import os
from typing import Any, Callable, Dict, Optional, Union
from xml.etree import ElementTree as etree

import toml
import yaml

from configmate import base


class ParserRegistry(base.BaseRegistry[Union[str, os.PathLike], Callable[[str], Any]]):
    """Holds a mapping from path patterns to parser functions."""


def create_path_matcher(pattern: str) -> Callable[[Union[str, os.PathLike]], bool]:
    """Create a function that matches a path against a pattern using `fnmatch`."""
    return lambda path: fnmatch.fnmatch(str(path), pattern)


### .INI
@ParserRegistry.register(create_path_matcher("*.ini"))
@ParserRegistry.register(create_path_matcher("*.INI"))
def parse_ini(text: str) -> Any:
    (cnfparser := configparser.ConfigParser()).read_string(text)
    return convert_ini_to_dict(cnfparser)


def convert_ini_to_dict(cnfparser: configparser.ConfigParser) -> Dict[str, Dict]:
    return {section: dict(cnfparser[section]) for section in cnfparser.sections()}


### .JSON
@ParserRegistry.register(create_path_matcher("*.json"))
@ParserRegistry.register(create_path_matcher("*.JSON"))
def parse_json(text: str) -> Any:
    return json.loads(text)


### .XML
@ParserRegistry.register(create_path_matcher("*.xml"))
@ParserRegistry.register(create_path_matcher("*.XML"))
def parse_xml(text: str) -> "Tree":
    root = etree.fromstring(text)
    return convert_etree_to_dict(root)


Tree = Optional[Union[str, Dict[str, "Tree"]]]


def convert_etree_to_dict(element: etree.Element) -> Tree:
    if not (children := list(element)):
        return element.text
    return {
        child.tag: child.text if not list(child) else convert_etree_to_dict(child)
        for child in children
    }


### .TOML
@ParserRegistry.register(create_path_matcher("*.toml"))
@ParserRegistry.register(create_path_matcher("*.tml"))
@ParserRegistry.register(create_path_matcher("*.TOML"))
@ParserRegistry.register(create_path_matcher("*.TML"))
def parse_toml(text: str) -> Dict[str, Any]:
    return toml.loads(text)


### .YAML
@ParserRegistry.register(create_path_matcher("*.yaml"))
@ParserRegistry.register(create_path_matcher("*.yml"))
@ParserRegistry.register(create_path_matcher("*YAML"))
@ParserRegistry.register(create_path_matcher("*.YML"))
def parse_yaml_safe(text: str) -> Any:
    return yaml.safe_load(text)