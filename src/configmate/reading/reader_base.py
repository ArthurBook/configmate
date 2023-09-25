import abc


class StringReader(abc.ABC):
    """
    StringReaders are responsible for reading the config in form of a string.
    """

    def read(self) -> str:
        return self._read()

    @abc.abstractmethod
    def _read(self) -> str:
        pass


## TODO abstract class for reading CLI args
