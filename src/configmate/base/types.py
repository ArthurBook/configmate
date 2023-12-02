import os
import pathlib
from typing import Mapping, TypeVar, Union

T = TypeVar("T")

FilePath = Union[str, os.PathLike, pathlib.Path]
FilePathT = TypeVar("FilePathT", bound=FilePath)
NestedDict = Mapping[str, Union[T, "NestedDict[T]"]]

# fmt: off
class Unset: 'Used to mark a value that will be set.'
class Inferred: 'Marks a value that is inferred during runtime.'
class Sentinel: 'Used to catch exhausted iterators.'
SENTINEL = Sentinel()
# fmt: on
