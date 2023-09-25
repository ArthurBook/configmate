import os
from typing import Union


def read_file(file_path: Union[str, os.PathLike], encoding: str = "utf-8") -> str:
    with open(file_path, "r", encoding=encoding) as file:
        return file.read()
