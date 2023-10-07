from typing import Any, Generic, NewType, Optional, Protocol, Sequence, TypeVar

# A string that is meant to be parsed to a config mapping
ConfigLike = NewType("ConfigLikeString", str)
FileExtension = NewType("FileExtension", str)

T_contra = TypeVar("T_contra", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


### Low level interfaces
class Source(Protocol, Generic[T_co]):
    def read(self) -> T_co:
        ...


class ConfigReader(Protocol, Generic[T_contra]):
    def read_config(self, source: Source[T_contra]) -> Any:
        ...


class FileInterpolator(Protocol):
    def interpolate(self, text: str) -> ConfigLike:
        ...


class FileParser(Protocol):
    def parse(self, text: ConfigLike) -> Any:
        ...


class Aggregator(Protocol):
    def aggregate(self, items: Sequence[Any]) -> Any:
        ...


class Validator(Protocol):
    def validate(self, item: Any) -> Any:
        ...
