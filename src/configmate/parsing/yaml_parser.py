import abc
from configmate.parsing import parser_base


class YamlParserBase(abc.ABC):
    def __init__(self) -> None:
        super().__init__()
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "YamlParsers require pyyaml to be installed. "
                "Please install the yaml extension through"
                "`pip install configmate[yaml]`."
            ) from exc
        self.yaml = yaml
