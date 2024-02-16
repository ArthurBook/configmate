import os
import pathlib
from typing import Mapping, Protocol, Sequence, TypeVar, Union

T = TypeVar("T")

FilePathTypes = (str, os.PathLike, pathlib.Path)
FilePath = Union[str, os.PathLike, pathlib.Path]
CliArgs = Sequence[str]
NestedDict = Mapping[str, Union[T, "NestedDict[T]"]]


class Unset:
    "Used to mark a value that will be set."


class Infer:
    "Marks a value that is inferred during runtime."


class Sentinel:
    "Used to catch exhausted iterators."


SENTINEL = Sentinel()


class HasDescription(Protocol):
    @classmethod
    def describe(cls) -> str: ...
