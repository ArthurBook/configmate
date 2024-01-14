import pathlib
from typing import Iterable, Iterator, Optional, Sequence, Tuple, TypeVar, Union

from configmate.base import operators, types

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
U = TypeVar("U")
U_contra = TypeVar("U_contra", contravariant=True)
V = TypeVar("V")


def compose_cli_processor(
    section_reader: operators.Operator[types.CliArgs, Sequence[str]],
    filepath_selector: operators.Operator[types.CliArgs, Iterable[types.FilePath]],
    file_parser: operators.Operator[types.FilePath, T_co],
    kwarg_selector: operators.Operator[types.CliArgs, Iterable[Tuple[str, str]]],
    kwarg_parser: operators.Operator[Tuple[str, str], T_co],
) -> operators.Operator[types.CliArgs, Iterator[T_co]]:
    return section_reader.pipe_to(
        operators.ChainOutputs(  # itertools.chain over the outputs of the following:
            operators.JoinOutputs(  # join: parsed files, then parsed args
                filepath_selector.pipe_to(operators.MapIterable(file_parser)),
                kwarg_selector.pipe_to(operators.MapIterable(kwarg_parser)),
            )
        )
    )


def compose_file_processor(
    path_validator: operators.Operator[types.FilePath, pathlib.Path],
    file_reader: operators.Operator[pathlib.Path, str],
    interpolator: Optional[operators.Operator[str, str]],
    parser: operators.Operator[str, T],
    section_selector: Optional[operators.Operator[T, U]],
) -> Union[
    operators.Operator[types.FilePath, T], operators.Operator[types.FilePath, U]
]:
    return (
        path_validator.pipe_to(file_reader)  # reads in the file as a string
        .pipe_to(interpolator)  # OPTIONAL: interpolate the string file
        .pipe_to(parser)  # parse the file into an object
        .pipe_to(section_selector)  # OPTIONAL: select the section from the config
    )


def compose_config_merger(
    aggregator: operators.Operator[Iterable[T_contra], U_contra],
    validator: Optional[operators.Operator[U_contra, V]],
) -> Union[
    operators.Operator[Iterable[T_contra], U_contra],
    operators.Pipeline[Iterable[T_contra], V],
]:
    return aggregator.pipe_to(validator)  # validator may be none
