try:
    import toml
except ImportError:
    _HAS_TOML_EXTENSION_INSTALLED = False
else:
    _HAS_TOML_EXTENSION_INSTALLED = True

from typing import Any
from configmate import exceptions
from configmate.parsing import base_parser


class TomlParser(base_parser.BaseConfigParser):
    def __init__(self) -> None:
        if not _HAS_TOML_EXTENSION_INSTALLED:
            raise exceptions.NeedsExtension(
                "TomlParsers require toml to be installed. "
                "Please install the toml extension through "
                "`pip install configmate[toml]`."
            )
        super().__init__()

    def _parse(self, data: str) -> Any:
        return toml.loads(data)
