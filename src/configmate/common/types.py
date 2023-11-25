import os
from typing import Any, Callable, Generic, Mapping, Protocol, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
FilePath = Union[str, os.PathLike]

InterpolationStrategy = Callable[[str], str]
ParsingStrategy = Callable[[str], T]
ValidationStrategy = Callable[[Any], T]

RecursiveMapping = Mapping[str, Union[T_co, "RecursiveMapping"]]

# fmt: off
class Inferred: 'Marks a value that is inferred during runtime.'
class Sentinel:
    'Used to catch exhausted iterators.'
    def __iter__(self) -> 'Sentinel': return self # pylint: disable=multiple-statements
    def __next__(self) -> 'Sentinel': return self # pylint: disable=multiple-statements
SENTINEL = Sentinel()

class Unset: 'Used to mark a value that will be set.'
# fmt: on


class RegistryProtocol(Protocol, Generic[T_contra, T_co]):
    """A registry that maps keys to values."""

    # fmt: off
    def __getitem__(self, key: T_contra) -> T_co: ...
    # fmt: on
