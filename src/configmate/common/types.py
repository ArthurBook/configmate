import os
from typing import Any, Callable, Generic, Protocol, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
FilePath = Union[str, os.PathLike]

ParsingStrategy = Callable[[str], T]
ValidationStrategy = Callable[[Any], T]

# fmt: off
class Inferred: 'Marks a value that is inferred during runtime.'
class Sentinel: 'Used to catch exhausted iterators.'
class Unset: 'Used to mark a value that will be set.'
# fmt: on


class RegistryProtocol(Protocol, Generic[T_contra, T_co]):
    """A registry that maps keys to values."""

    # fmt: off
    def __getitem__(self, key: T_contra) -> T_co: ...
    # fmt: on


class ValidatorProtocol(Protocol, Generic[T_co]):
    """A validator that can be used to validate a value."""

    # fmt: off
    def __call__(self, value: Any) -> T_co: ...
    # fmt: on
