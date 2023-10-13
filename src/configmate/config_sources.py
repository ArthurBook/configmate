import pathlib

from configmate import interface as i


class FileReader(i.Source[i.ConfigLike]):
    """
    Allows you to read a file
    """

    def __init__(self, path: i.PathLikeString, encoding: str = "utf-8") -> None:
        super().__init__()
        self.path = path
        self.encoding = encoding

    def read(self) -> i.ConfigLike:
        return i.ConfigLike(pathlib.Path(self.path).read_text(self.encoding))
