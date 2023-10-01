try:
    import yaml
except ImportError:
    _HAS_YAML_EXTENSION_INSTALLED = False
else:
    _HAS_YAML_EXTENSION_INSTALLED = True

import abc
from typing import Any, Set
from configmate import exceptions
from configmate.parsing import base_parser


class YamlParserBase(abc.ABC):
    def __init__(self) -> None:
        if not _HAS_YAML_EXTENSION_INSTALLED:
            raise exceptions.NeedsExtension(
                "YamlParsers require pyyaml to be installed. "
                "Please install the yaml extension through "
                "`pip install configmate[yaml]`."
            )
        super().__init__()

    def _parse(self, data: str) -> Any:
        return self._parse_yaml(data)

    @abc.abstractmethod
    def _parse_yaml(self, data: str) -> Any:
        ...


class YamlSafeLoadParser(YamlParserBase, base_parser.InferableConfigParser):
    def _parse_yaml(self, data: str) -> Any:
        return yaml.safe_load(data)

    @classmethod
    def supported_file_extensions(cls) -> Set[str]:
        return {".yaml", ".yml"}


# dont infer this parser
class YamlUnSafeLoadParser(YamlParserBase, base_parser.BaseConfigParser):
    def _parse_yaml(self, data: str) -> Any:
        return yaml.full_load(data)
