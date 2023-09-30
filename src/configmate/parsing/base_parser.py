import abc
from typing import Any, Mapping


class BaseParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, data: str) -> Any:
        ...


class BaseConfigParser(BaseParser, abc.ABC):
    def parse(self, data: str) -> Mapping[str, Any]:
        parsed_data = self._parse(data)
        self.validate_parsed_data(parsed_data)
        return parsed_data

    @abc.abstractmethod
    def _parse(self, data: str) -> Mapping[str, Any]:
        ...

    def validate_parsed_data(self, parsed_data: Mapping[str, Any]) -> None:
        assert isinstance(parsed_data, Mapping), "Parsed data must be a mapping"
