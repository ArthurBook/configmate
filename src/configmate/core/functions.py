import functools
import itertools
from typing import Any, Callable, Optional, TypeVar, Union, overload

from configmate.base import constants, operators, types
from configmate.components import (
    aggregators,
    interpolators,
    parsers,
    selectors,
    validators,
)
from configmate.core import builders

T = TypeVar("T")
U = TypeVar("U")


# fmt: off
@overload
def get_config( # if no validation is specified, we get the output of the aggregation
    *config_files: types.FilePath,
    ## file reading
    interpolation: Optional[interpolators.InterpolatorSpec] = constants.ENVIRONMENT,
    parsing: Union[types.Infer, parsers.ParsingSpec] = constants.INFER_FROM_PATH,
    section: Optional[selectors.SectionSelectionSpec] = None,
    aggregation: aggregators.AggregationSpec[T, U] = ...,
    validation: None = None,
    ## CLI overlay options
    cli_section_name: Optional[str] = None,
    cli_section_end: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    cli_overlay_file_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX,
    cli_overlay_arg_key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX,
    cli_overlay_arg_key_delimiter: str = constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
    cli_overlay_arg_parser: Callable[[str], Any] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
    ## encoding
    file_encoding: str = constants.SYS_DEFAULT_FILE_ENCODING,
) -> U: ...
@overload
def get_config( # the validation determines the return type
    *config_files: types.FilePath,
    ## file reading
    interpolation: Optional[interpolators.InterpolatorSpec] = constants.ENVIRONMENT,
    parsing: Union[types.Infer, parsers.ParsingSpec] = constants.INFER_FROM_PATH,
    section: Optional[selectors.SectionSelectionSpec] = None,
    aggregation: aggregators.AggregationSpec = constants.OVERLAY,
    validation: validators.ValidationSpec[T, U] = ...,
    ## CLI overlay options
    cli_section_name: Optional[str] = None,
    cli_section_end: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    cli_overlay_file_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX,
    cli_overlay_arg_key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX,
    cli_overlay_arg_key_delimiter: str = constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
    cli_overlay_arg_parser: Callable[[str], Any] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
    ## encoding
    file_encoding: str = constants.SYS_DEFAULT_FILE_ENCODING,
) -> U: ...
# fmt: on
def get_config(  # pylint: disable=too-many-arguments,too-many-locals
    *config_files: types.FilePath,
    ## file reading
    interpolation: Optional[interpolators.InterpolatorSpec] = constants.ENVIRONMENT,
    parsing: Union[types.Infer, parsers.ParsingSpec] = constants.INFER_FROM_PATH,
    section: Optional[selectors.SectionSelectionSpec] = None,
    aggregation: aggregators.AggregationSpec = constants.OVERLAY,
    validation: Optional[validators.ValidationSpec] = None,
    ## CLI overlay options
    cli_section_name: Optional[str] = None,
    cli_section_end: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    cli_overlay_file_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX,
    cli_overlay_arg_key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX,
    cli_overlay_arg_key_delimiter: str = constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
    cli_overlay_arg_parser: Callable[
        [str], Any
    ] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
    ## encoding
    file_encoding: str = constants.SYS_DEFAULT_FILE_ENCODING,
):
    """Get the config from the given files, with the given options."""
    file_processing_pipeline = builders.build_fileprocessor(
        interpolation=interpolation,
        parsing=parsing,
        section=section,
        file_encoding=file_encoding,
    )
    cli_reader = builders.build_cli_reader(
        section_name=cli_section_name,
        section_end=cli_section_end,
        file_arg_prefix=cli_overlay_file_prefix,
        cli_overlay_file_parser=file_processing_pipeline,
        kwarg_key_delimiter=cli_overlay_arg_key_delimiter,
        kwarg_key_prefix=cli_overlay_arg_key_prefix,
        kwarg_value_parser=cli_overlay_arg_parser,
    )
    config_merger = builders.build_config_merger(
        aggregation=aggregation,
        validation=validation,
    )
    return config_merger(
        itertools.chain(
            operators.MapIterable(file_processing_pipeline)(config_files),
            cli_reader(constants.CLI_ARGS),  # pylint: disable=not-callable
        )
    )


def configure(  # pylint: disable=too-many-arguments,too-many-locals
    *config_files: types.FilePath,
    ## file reading
    interpolation: Optional[interpolators.InterpolatorSpec] = constants.ENVIRONMENT,
    parsing: Union[types.Infer, parsers.ParsingSpec] = constants.INFER_FROM_PATH,
    section: Optional[selectors.SectionSelectionSpec] = None,
    aggregation: aggregators.AggregationSpec = constants.OVERLAY,
    validation: Optional[validators.ValidationSpec] = None,
    ## CLI overlay options
    cli_section_name: Optional[str] = None,
    cli_section_end: Optional[str] = constants.CLI_SECTION_END_TOKEN,
    cli_overlay_file_prefix: str = constants.CLI_OVERLAY_FILE_PREFIX,
    cli_overlay_arg_key_prefix: str = constants.CLI_OVERLAY_KWARG_KEY_PREFIX,
    cli_overlay_arg_key_delimiter: str = constants.CLI_OVERLAY_KWARG_KEY_DELIMITER,
    cli_overlay_arg_parser: Callable[
        [str], Any
    ] = constants.CLI_OVERLAY_KWARG_VAL_PARSER,
    ## encoding
    file_encoding: str = constants.SYS_DEFAULT_FILE_ENCODING,
) -> Callable[[Callable[..., U]], Callable[..., U]]:
    """Decorator to configure a function with the given config."""
    file_processing_pipeline = builders.build_fileprocessor(
        interpolation=interpolation,
        parsing=parsing,
        section=section,
        file_encoding=file_encoding,
    )
    cli_reader = builders.build_cli_reader(
        section_name=cli_section_name,
        section_end=cli_section_end,
        file_arg_prefix=cli_overlay_file_prefix,
        cli_overlay_file_parser=file_processing_pipeline,
        kwarg_key_delimiter=cli_overlay_arg_key_delimiter,
        kwarg_key_prefix=cli_overlay_arg_key_prefix,
        kwarg_value_parser=cli_overlay_arg_parser,
    )
    config_merger = builders.build_config_merger(
        aggregation=aggregation,
        validation=validation,
    )

    def decorator(func: Callable[..., U]) -> Callable[..., U]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> U:
            kwargs.update(dict(zip(func.__code__.co_varnames, args)))
            new_kwargs = config_merger(
                itertools.chain(
                    operators.MapIterable(file_processing_pipeline)(config_files),
                    cli_reader(constants.CLI_ARGS),  # pylint: disable=not-callable
                    (kwargs,),
                )
            )
            return func(**new_kwargs)

        return wrapper

    return decorator
