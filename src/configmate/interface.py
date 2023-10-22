import os
from typing import Any, Callable, Iterable, Type, TypeVar, Union

from typing_extensions import Annotated

# Type variables
T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

# For hinting
FilePath = Union[str, os.PathLike]
ConfigLike = Annotated[str, "ConfigLike"]
CliArg = str
CliArgArray = Iterable[CliArg]

## Generic interfaces
Interpolator = Callable[[str], ConfigLike]
Transformer = Callable[[T], U]
Aggregator = Callable[[T], U]
Validator = Callable[[T, Type[U]], U]

## Specific interfaces
FileReader = Transformer[FilePath, ConfigLike]
OverlayParser = Transformer[CliArgArray, Iterable[FilePath]]
Parser = Transformer[ConfigLike, Any]
OverrideParser = Transformer[CliArgArray, Iterable[Any]]
