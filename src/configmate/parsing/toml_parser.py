import abc
from configmate.parsing import parser_base


class TomlParserBase(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        try:
            import toml
        except ImportError as exc:
            raise ImportError(
                "TomlParsers requires toml to be installed. "
                "Please install the toml extension through "
                "`pip install configmate[toml]`."
            ) from exc
        self.toml = toml
