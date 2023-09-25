import abc
from typing import Any, Set
from configmate.configuration import configuration_base


class ConfigParser(abc.ABC):
    """
    ConfigParser is responsible for parsing the config in from a source.
    """

    def parse(self) -> Any:
        return self._parse()

    @abc.abstractmethod
    def _parse(self) -> Any:
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def parsertype(cls) -> configuration_base.SupportedParsers:
        """
        These are used for mapping the parser type to the parser class.
        """


class FileConfigParser(ConfigParser):
    """
    FileConfigParser is responsible for parsing the config in from a file.
    """

    @classmethod
    @property
    @abc.abstractmethod
    def extension(cls) -> Set[str]:
        """
        These are used for inferring the parser type from the file extension.
        """
