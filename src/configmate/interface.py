import os
from typing import Any, Generic, Iterable, NewType, Protocol, Sequence, TypeVar, Union

# A string that is meant to be parsed to a config mapping
PathLikeString = Union[str, os.PathLike]
ConfigLike = NewType("ConfigLike", str)
CliArg = str
CliArgArray = Iterable[str]
FileExtension = NewType("FileExtension", str)

# Type variables
T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


### Simple interfaces
class HasBool(Protocol):
    def __bool__(self) -> bool:
        ...


### Low level interfaces
class Source(Protocol, Generic[T_co]):
    def read(self) -> T_co:
        ...


class ConfigReader(Protocol, Generic[T_contra, T_co]):
    def read_config(self, source: T_contra) -> T_co:
        ...


class FileInterpolator(Protocol):
    def interpolate(self, text: str) -> ConfigLike:
        ...


class Parser(Protocol):
    def parse(self, text: ConfigLike) -> Any:
        ...


class Aggregator(Protocol):
    def aggregate(self, items: Sequence[Any]) -> Any:
        ...


class Validator(Protocol):
    def validate(self, item: Any) -> Any:
        ...
