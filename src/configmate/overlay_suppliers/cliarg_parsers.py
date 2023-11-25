import json
from typing import Callable, Generic, Iterable, Iterator, List, TypeVar

from configmate import _utils, base, config_sources
from configmate.overlay_suppliers import cliarg_filters

DEFAULT_ARG_KEY_SPLIT_TOKEN = "."  # splits +foo.bar to (foo, bar)
DEFAULT_ARG_PARSER = json.loads  # JSON

T = TypeVar("T")
V = TypeVar("V", bound=base.BaseSource[str])


###
# config file overlay reading
###
class CliFilePathParser(base.HasDescription):
    __slots__ = ("file_factory_method", "prefix_len")

    def __init__(
        self,
        prefix_len: int = len(cliarg_filters.DEFAULT_FILE_PREFIX),
        file_encoding: str = config_sources.DEFAULT_FILE_ENCODING,
    ) -> None:
        super().__init__()
        self.encoding = file_encoding
        self.prefix_len = prefix_len

    def __call__(self, unparsed_path: str) -> config_sources.File:
        return config_sources.File(str(unparsed_path)[self.prefix_len :], self.encoding)


class OverlayFileSupplier(base.BaseOverlayFileSupplier):
    def __init__(
        self,
        cli_arg_stream: Iterable[str] = cliarg_filters.ArgSelector(),
        parser: Callable[[str], base.BaseSource[str]] = CliFilePathParser(),
    ) -> None:
        super().__init__()
        self.cli_arg_stream = cli_arg_stream
        self.parser = parser

    def get_overlays(self) -> Iterable[base.BaseSource[str]]:
        return map(self.parser, self.cli_arg_stream)


###
# arg overlay argument reading
###
class CliOverlayArgumentKeyParser(base.HasDescription):
    __slots__ = ("prefix_len", "split_token")

    def __init__(
        self,
        key_prefix_len: int = len(cliarg_filters.DEFAULT_KWARG_PREFIX),
        split_token: str = DEFAULT_ARG_KEY_SPLIT_TOKEN,
    ) -> None:
        self.prefix_len = key_prefix_len
        self.split_token = split_token

    def __call__(self, unparsed_key: str) -> List[str]:
        return unparsed_key[self.prefix_len :].split(self.split_token)


class OverlayArgSupplier(base.BaseArgOverlaySupplier[T], Generic[T]):
    __slots__ = ("args", "key_parser", "val_parser")

    def __init__(
        self,
        args: Iterable[str] = cliarg_filters.KeyValueSelector(),
        key_parser: Callable[[str], Iterable[str]] = CliOverlayArgumentKeyParser(),
        value_parser: Callable[[str], T] = DEFAULT_ARG_PARSER,
    ) -> None:
        super().__init__()
        self.args = args
        self.key_parser = key_parser
        self.val_parser = value_parser

    def get_overlays(self) -> Iterator[base.RecursiveMapping[T]]:
        for key, value in _utils.iterate_window(self.args, 2, 2):
            yield _utils.make_nested_dict(self.key_parser(key), self.val_parser(value))
