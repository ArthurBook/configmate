import abc
import os
import pathlib
from typing import Any, Collection, Dict, Mapping, Type, Union

from configmate import exceptions


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
        if not isinstance(parsed_data, Mapping):
            raise exceptions.InvalidConfigError(
                "Parsed data must be a mapping. try using a different parser"
                f" that allows for root type: {type(parsed_data)}"
            )


class InferableConfigParser(BaseConfigParser, abc.ABC):
    __registry__: Dict[str, Type[BaseConfigParser]] = dict()

    @classmethod
    @abc.abstractmethod
    def supported_file_extensions(cls) -> Collection[str]:
        ...

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        inferable_parsers = cls.get_parser_mapping()
        assert all(extension.startswith(".") for extension in inferable_parsers.keys())
        if overlap := set(inferable_parsers).intersection(set(cls.__registry__)):
            raise exceptions.DuplicateParsers(f"Duplicate parsers for {overlap=}")
        InferableConfigParser.__registry__.update(inferable_parsers)

    @classmethod
    def infer_parser_from_filepath(
        cls, filepath_or_extension: Union[str, os.PathLike]
    ) -> Type[BaseConfigParser]:
        file_extension = pathlib.Path(filepath_or_extension).suffix
        return cls.infer_parser_from_fileextension(file_extension)

    @classmethod
    def infer_parser_from_fileextension(
        cls, file_extension: str
    ) -> Type[BaseConfigParser]:
        key = file_extension.lower()
        if (parser := InferableConfigParser.__registry__.get(key)) is None:
            raise exceptions.NeedsExtension(f"No parsers for {file_extension=}")
        return parser

    @classmethod
    def get_parser_mapping(cls) -> Dict[str, Type[BaseConfigParser]]:
        return {ext.lower(): cls for ext in cls.supported_file_extensions()}
