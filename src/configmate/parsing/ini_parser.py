from configparser import ConfigParser
from typing import Any
from configmate.parsing import base_parser


class IniParser(base_parser.BaseConfigParser):
    def __init__(self, configparser: ConfigParser) -> None:
        super().__init__()
        self.configparser = configparser

    def _parse(self, data: str) -> Any:
        self.configparser.read_string(data)
        return convert_to_dict(self.configparser)


def convert_to_dict(configparser: ConfigParser) -> Any:
    return {section: dict(configparser[section]) for section in configparser.sections()}
