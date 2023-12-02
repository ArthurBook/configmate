""" Filereading step for the pipeline
"""
import pathlib

from configmate.base import operators, types


class FileReader(operators.Operator[types.FilePath, str]):
    def __init__(self, encoding: str = "utf-8") -> None:
        super().__init__()
        self.encoding = encoding

    def _transform(self, ctx: operators.Context, input_: types.FilePath) -> str:
        return pathlib.Path(input_).read_text(encoding=self.encoding)
