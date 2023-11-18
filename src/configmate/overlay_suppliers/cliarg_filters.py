import itertools
import re
from typing import Callable, Generator, Iterable, Iterator

from configmate import _utils, base, config_sources

DEFAULT_OVERLAY_STREAM = config_sources.CommandLineArgs()
DEFAULT_KWARG_PREFIX = "+"  # for example: "+foo.bar value"
DEFAULT_FILE_PREFIX = "++"  # for example: "++path/to/file.yaml"
DEFAULT_SECTION_END = "/"  # for example: Raxban +i 1 ++ping/pong / Haxban ..."


###
# Regex helpers
###
class RegexTrigger(base.HasDescription):
    __slots__ = ("pattern",)

    def __init__(self, prefix: str) -> None:
        escaped_prefix = re.escape(prefix)
        self.pattern = re.compile(f"^{escaped_prefix}([^{escaped_prefix}]|$)")

    def __call__(self, arg: str) -> bool:
        return self.pattern.search(arg) is not None


###
# Filters for command line arguments
###
class SectionFilter(base.BaseCliArgFilter):
    """Filters out command line arguments that are not in a section."""

    def __init__(
        self,
        arg_stream: Iterable[str] = DEFAULT_OVERLAY_STREAM,
        start_finder: Callable[[str], bool] = lambda _: True,
        end_finder: Callable[[str], bool] = RegexTrigger(DEFAULT_SECTION_END),
    ) -> None:
        self.unfiltered_args = arg_stream
        self.section_start_finder = start_finder
        self.section_end_finder = end_finder

    def __iter__(self) -> Iterator[str]:
        section_tracker = self.in_section()
        next(section_tracker)  # prime
        return filter(section_tracker.send, self.unfiltered_args)

    def in_section(self, _arg: str = "") -> Generator[bool, str, None]:
        while not self.section_start_finder(_arg):
            _arg = yield False
        while not self.section_end_finder(_arg):
            _arg = yield True
        yield True  # for the last item


class ArgSelector(base.BaseCliArgFilter):
    """Filters out command line arguments using a callable."""

    def __init__(
        self,
        arg_stream: Iterable[str] = DEFAULT_OVERLAY_STREAM,
        filter_: Callable[[str], bool] = RegexTrigger(DEFAULT_FILE_PREFIX),
    ) -> None:
        self.unfiltered_args = arg_stream
        self.filter = filter_

    def __iter__(self) -> Iterator[str]:
        return filter(self.filter, self.unfiltered_args)


class KeyValueSelector(base.BaseCliArgFilter):
    """Filters out command line arguments using a callable that takes a key and a value."""

    def __init__(
        self,
        arg_stream: Iterable[str] = DEFAULT_OVERLAY_STREAM,
        key_filter: Callable[[str], bool] = RegexTrigger(DEFAULT_KWARG_PREFIX),
    ) -> None:
        self.unfiltered_args = arg_stream
        self.filter_ = key_filter

    def __iter__(self) -> Iterator[str]:
        sliding_window = _utils.iterate_window(self.unfiltered_args, 2)
        pairs = ((k, v) for k, v in sliding_window if self.filter_(k))
        return itertools.chain.from_iterable(pairs)
