import dataclasses
import os
import pathlib
import sys
from typing import Iterator, List, Union

from configmate import base


DEFAULT_FILE_ENCODING = "utf-8"


### File reading from disk
@dataclasses.dataclass(frozen=True)
class File(base.BaseSource[str]):
    path: Union[str, os.PathLike]
    encoding: str = DEFAULT_FILE_ENCODING

    def read(self) -> str:
        return pathlib.Path(self.path).read_text(self.encoding)


def ensure_file(file: Union[str, os.PathLike, File]) -> File:
    if isinstance(file, (str, os.PathLike)):
        return File(file)
    assert isinstance(file, File), f"Expected File or path, got {type(file)}:{file=}"
    return file


### Comand line arguments
@dataclasses.dataclass
class CommandLineArgs(base.BaseSource[List[str]]):
    command_line_args: List[str] = dataclasses.field(default_factory=lambda: sys.argv)

    def read(self) -> List[str]:
        return self.command_line_args

    def __iter__(self) -> Iterator[str]:
        return iter(self.read())
