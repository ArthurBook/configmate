import pathlib
from typing import Callable, Iterable, Iterator, Optional, TypeVar, Union

from configmate.base import constants, operators, types
from configmate.components import (
    aggregators,
    cli_readers,
    filereader,
    interpolators,
    parsers,
    selectors,
    validators,
)
from configmate.core import composers

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
U_contra = TypeVar("U_contra", contravariant=True)
U = TypeVar("U")
V = TypeVar("V")

build_interpolator = interpolators.InterpolatorFactory.build_interpolator
build_parser = parsers.ParserFactory.build_parser
build_runtime_inferred_parser = parsers.ParserFactory.infer_from
build_config_section_selector = selectors.SectionSelectorFactory.build_selector
build_aggregator = aggregators.AggregatorFactory.build_aggregator
build_validator = validators.TypeValidatorFactory.build_validator


def build_cli_reader(
    cli_overlay_file_parser: operators.Operator[types.FilePath, T_co],
    file_arg_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX,
    section_name: Optional[str] = None,
    section_end: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    kwarg_key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX,
    kwarg_key_delimiter: str = constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
    kwarg_value_parser: Callable[[str], T] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
) -> operators.Operator[types.CliArgs, Iterator[Union[types.NestedDict[T], T_co]]]:
    return composers.compose_cli_processor(
        section_reader=cli_readers.CliSectionReader(section_name, section_end),
        filepath_selector=cli_readers.ArgSelector(file_arg_prefix),
        file_parser=cli_overlay_file_parser,
        kwarg_selector=cli_readers.KeyValueSelector(kwarg_key_prefix),
        kwarg_parser=cli_readers.DictParser(kwarg_key_delimiter, kwarg_value_parser),
    )


def build_fileprocessor(
    interpolation: Optional[interpolators.InterpolatorSpec] = constants.ENVIRONMENT,
    parsing: Union[types.Infer, parsers.ParsingSpec[T]] = constants.INFER_FROM_PATH,
    section: Optional[selectors.SectionSelectionSpec[T, U]] = None,
    file_encoding: str = constants.SYS_DEFAULT_FILE_ENCODING,
) -> Union[
    operators.Operator[types.FilePath, T], operators.Operator[types.FilePath, U]
]:
    return composers.compose_file_processor(
        path_validator=(path_factory := validators.FunctionValidator(pathlib.Path)),
        file_reader=filereader.FileReader(encoding=file_encoding),
        interpolator=(
            build_interpolator(interpolation) if interpolation is not None else None
        ),
        parser=(
            build_runtime_inferred_parser(path_factory)
            if isinstance(parsing, types.Infer)
            else build_parser(parsing)
        ),
        section_selector=(
            build_config_section_selector(section) if section is not None else None
        ),
    )


def build_config_merger(
    aggregation: aggregators.AggregationSpec[T_contra, U],
    validation: Optional[validators.ValidationSpec[U, V]] = None,
) -> Union[
    operators.Operator[Iterable[T_contra], U],
    operators.Pipeline[Iterable[T_contra], V],
]:
    return composers.compose_config_merger(
        build_aggregator(aggregation),
        build_validator(validation) if validation is not None else None,
    )
