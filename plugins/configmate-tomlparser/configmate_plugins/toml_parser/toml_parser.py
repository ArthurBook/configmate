"""This is a plugin for configmate that adds support for TOML files.
"""

from typing import Any

import toml

from configmate.base import operators
from configmate.components import parsers

TOML_EXTENSIONS = ".tml", ".toml", ".TML", ".TOML"


class TomlParser(parsers.Parser[Any]):
    def _transform(self, ctx: operators.Context, input_: Any) -> Any:
        return toml.loads(input_)


parsers.FileFormatParserRegistry.add_strategy(TomlParser, *TOML_EXTENSIONS)
