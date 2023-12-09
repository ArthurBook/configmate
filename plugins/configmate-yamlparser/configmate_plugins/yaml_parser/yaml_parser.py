"""This is a plugin for configmate that adds support for TOML files.
"""
from typing import Any

import yaml

from configmate.base import operators
from configmate.components import parsers

YAML_EXTENSIONS = ".yml", ".yaml", ".YML", ".YAML"


class YamlParser(parsers.Parser[Any]):
    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        return yaml.safe_load(input_)


# Register the parser with configmate
parsers.FileFormatParserRegistry.add_strategy(YamlParser, *YAML_EXTENSIONS)
