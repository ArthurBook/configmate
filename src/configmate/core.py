import os
from typing import Generic, Iterable, TypeVar, Union

from configmate import base
from configmate import config_sources as _config_sources
from configmate import interpolation as _interpolation
from configmate import overlay_suppliers as _overlay_suppliers
from configmate import parsing as _parsing
from configmate import section_selection as _section_selection


class _InferParser:
    """"""


DEFAULT_INTERPOLATION = _interpolation.EnvInterpolator()
INFER_PARSER_FROM_FILEPATH = _InferParser()


T = TypeVar("T")
U = TypeVar("U")


class CliOptions(
    _overlay_suppliers.OverlayArgOptions,
    _overlay_suppliers.OverlayFileOptions,
    total=False,
):
    ...


class ConfigHandler(base.HasDescription, Generic[T, U]):
    """Handles config objects."""

    def __init__(
        self,
        configs: Iterable[T],
        aggregator: base.BaseAggregator,
        validator: base.BaseValidator[U],
    ) -> None:
        super().__init__()
        self.configs = configs
        self.aggregator = aggregator
        self.validator = validator

    def get_config(self) -> U:
        aggregated_config = self.aggregator.aggregate(self.configs)
        return self.validator.validate(aggregated_config)


class ConfigFileProcessor(base.HasDescription, Generic[T]):
    """Processes a config source and returns a config object."""

    def __init__(
        self,
        file: base.BaseSource[str],
        interpolator: base.BaseInterpolator,
        parser: base.BaseParser[T],
        section_selector: base.BaseSectionSelector[T],
    ) -> None:
        super().__init__()
        self.file = file
        self.interpolator = interpolator
        self.parser = parser
        self.section_selector = section_selector

    def get_config(self) -> T:
        raw_config = self.file.read()
        interpolated_config = self.interpolator.interpolate(raw_config)
        parsed_config = self.parser.parse(interpolated_config)
        return self.section_selector.select(parsed_config)


def make_config_processor(
    file: Union[str, os.PathLike, _config_sources.File],
    interpolator: _interpolation.InterpolationSpec = DEFAULT_INTERPOLATION,
    parser: Union[_InferParser, _parsing.ParsingSpec[T]] = INFER_PARSER_FROM_FILEPATH,
    section_selector: _section_selection.SectionSelectionSpec = None,
) -> ConfigFileProcessor[T]:
    file = _config_sources.ensure_file(file)
    interpolator = _interpolation.make_interpolator(interpolator)
    parser = _parsing.make_parser(file if isinstance(parser, _InferParser) else parser)
    section_selector = _section_selection.make_sectionselector(section_selector)
    return ConfigFileProcessor(file, interpolator, parser, section_selector)
