from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Literal,
    Optional,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import TypedDict

from configmate import _utils, base, config_sources
from configmate.overlay_suppliers import cliarg_filters, cliarg_parsers

T = TypeVar("T")
U = TypeVar("U", bound=cliarg_parsers.OverlayFileSupplier)
V = TypeVar("V", bound=cliarg_parsers.OverlayArgSupplier)


###
# section options
###
class SectionOptions(TypedDict, total=False):
    section_name: str
    section_end_token: str


def make_cli_section_iterator(
    section_name: Optional[str] = None,
    end_token: str = cliarg_filters.DEFAULT_SECTION_END,
    **_,  # ignore unexpected kwargs
) -> Union[config_sources.CommandLineArgs, cliarg_filters.SectionFilter]:
    if section_name is None:
        return cliarg_filters.DEFAULT_OVERLAY_STREAM
    return cliarg_filters.SectionFilter(
        arg_stream=cliarg_filters.DEFAULT_OVERLAY_STREAM,
        start_finder=cliarg_filters.RegexTrigger(section_name),
        end_finder=cliarg_filters.RegexTrigger(end_token),
    )


###
# file overlay reader factory
###
class OverlayFileOptions(SectionOptions, total=False):
    file_arg_prefix: str
    file_encoding: str


OverlayFileSpec = Union[
    Literal[None],
    base.BaseOverlayFileSupplier,
    str,
    OverlayFileOptions,
]

is_file_overlay_supplier = _utils.make_typecheck(base.BaseOverlayFileSupplier)


# fmt: off
@overload
def construct_file_supplier(spec: OverlayFileSpec) -> base.BaseOverlayFileSupplier:
    '''TODO docs
    '''
@overload
def construct_file_supplier(spec: Literal[None]) -> base.BaseOverlayFileSupplier: ...
@overload
def construct_file_supplier(spec: base.BaseOverlayFileSupplier) -> base.BaseOverlayFileSupplier: ... # pylint: disable=line-too-long
@overload
def construct_file_supplier(spec: str) -> base.BaseOverlayFileSupplier: ...
@overload
def construct_file_supplier(spec: OverlayFileOptions) -> base.BaseOverlayFileSupplier: ...
# fmt: on
def construct_file_supplier(spec: OverlayFileSpec) -> base.BaseOverlayFileSupplier:
    return OverlayFileSupplierFactoryRegistry.get_strategy(spec)(spec)


class OverlayFileSupplierFactoryRegistry(
    base.BaseMethodStore[OverlayFileSpec, base.BaseOverlayFileSupplier]
):
    """A registry of methods for constructing overlay file readers from a CLI argument."""


@OverlayFileSupplierFactoryRegistry.register(_utils.is_none)
def get_default_file_supplier(_: None) -> cliarg_parsers.OverlayFileSupplier:
    return cliarg_parsers.OverlayFileSupplier()


@OverlayFileSupplierFactoryRegistry.register(is_file_overlay_supplier)
def pass_through_file_overlay_supplier(file_supplier: U) -> U:
    return file_supplier


@OverlayFileSupplierFactoryRegistry.register(_utils.is_string)
def make_file_supplier_from_string(section_name: str) -> base.BaseOverlayFileSupplier:
    return make_file_supplier({"section_name": section_name})


@OverlayFileSupplierFactoryRegistry.register(_utils.is_dict)
def make_file_supplier(spec: OverlayFileOptions) -> cliarg_parsers.OverlayFileSupplier:
    section = make_cli_section_iterator(**spec)
    section_args = make_cli_arg_iterator(section, **spec)
    return make_file_overlay_supplier(section_args, **spec)


def make_file_overlay_supplier(
    arg_stream: Iterable[str],
    file_arg_prefix: str = cliarg_filters.DEFAULT_FILE_PREFIX,
    file_encoding: str = config_sources.DEFAULT_FILE_ENCODING,
    **_,  # ignore unexpected kwargs
) -> cliarg_parsers.OverlayFileSupplier:
    pathparser = cliarg_parsers.CliFilePathParser(len(file_arg_prefix), file_encoding)
    return cliarg_parsers.OverlayFileSupplier(arg_stream, pathparser)


def make_cli_arg_iterator(
    arg_stream: Iterable[str],
    file_arg_prefix: str = cliarg_filters.DEFAULT_FILE_PREFIX,
    **_,  # ignore unexpected kwargs
) -> cliarg_filters.ArgSelector:
    return cliarg_filters.ArgSelector(
        arg_stream=arg_stream,
        filter_=cliarg_filters.RegexTrigger(file_arg_prefix),
    )


###
# arg overlay reader factory
###
class OverlayArgOptions(SectionOptions, Generic[T], total=False):
    key_prefix: str
    key_split_token: str
    value_parser: Callable[[str], T]


OverlayArgSpec = Union[
    Literal[None],
    str,
    OverlayArgOptions[T],
    base.BaseArgOverlaySupplier[T],
]

is_arg_overlay_supplier = _utils.make_typecheck(base.BaseArgOverlaySupplier)


# fmt: off
@overload
def construct_arg_supplier(spec: OverlayArgSpec[T]) -> base.BaseArgOverlaySupplier[T]:
    '''TODO docs
    '''
@overload
def construct_arg_supplier(spec: Literal[None]) -> cliarg_parsers.OverlayArgSupplier[Any]: ...
@overload
def construct_arg_supplier(spec: str) -> cliarg_parsers.OverlayArgSupplier[Any]: ...
@overload
def construct_arg_supplier(spec: cliarg_parsers.OverlayArgSupplier[T]) -> cliarg_parsers.OverlayArgSupplier[T]: ... # pylint: disable=line-too-long
@overload
def construct_arg_supplier(spec: base.BaseArgOverlaySupplier[T]) -> base.BaseArgOverlaySupplier[T]: ... # pylint: disable=line-too-long
# fmt: on
def construct_arg_supplier(spec: OverlayArgSpec) -> base.BaseArgOverlaySupplier:
    return OverlayArgSupplierFactoryRegistry.get_strategy(spec)(spec)


class OverlayArgSupplierFactoryRegistry(
    base.BaseMethodStore[OverlayArgSpec[T], base.BaseArgOverlaySupplier[T]]
):
    """A registry of methods for constructing overlay file readers from a CLI argument."""


@OverlayArgSupplierFactoryRegistry.register(_utils.is_none)
def get_default_arg_supplier(_: None) -> cliarg_parsers.OverlayArgSupplier:
    return cliarg_parsers.OverlayArgSupplier()


@OverlayArgSupplierFactoryRegistry.register(is_arg_overlay_supplier)
def pass_through_arg_overlay_supplier(arg_supplier: V) -> V:
    return arg_supplier


@OverlayArgSupplierFactoryRegistry.register(_utils.is_string)
def make_section_arg_supplier(section_name: str) -> base.BaseArgOverlaySupplier:
    return make_arg_supplier({"section_name": section_name})


@OverlayArgSupplierFactoryRegistry.register(_utils.is_dict)
def make_arg_supplier(spec: OverlayArgOptions[T]) -> base.BaseArgOverlaySupplier[T]:
    section = make_cli_section_iterator(**spec)
    return cliarg_parsers.OverlayArgSupplier(
        args=make_cli_key_value_iterator(section, **spec),
        key_parser=make_overlay_arg_key_parser(**spec),
        value_parser=make_overlay_arg_val_parser(**spec),
    )


def make_overlay_arg_key_parser(
    key_prefix: str = cliarg_filters.DEFAULT_KWARG_PREFIX,
    key_split_token: str = cliarg_parsers.DEFAULT_ARG_KEY_SPLIT_TOKEN,
    **_,  # ignore unexpected kwargs
) -> cliarg_parsers.CliOverlayArgumentKeyParser:
    return cliarg_parsers.CliOverlayArgumentKeyParser(len(key_prefix), key_split_token)


def make_overlay_arg_val_parser(
    value_parser: Callable[[str], T] = cliarg_parsers.DEFAULT_ARG_PARSER,
    **_,  # ignore unexpected kwargs
) -> Callable[[str], T]:
    return value_parser


def make_cli_key_value_iterator(
    arg_stream: Iterable[str],
    key_prefix: str = cliarg_filters.DEFAULT_KWARG_PREFIX,
    **_,  # ignore unexpected kwargs
) -> cliarg_filters.KeyValueSelector:
    return cliarg_filters.KeyValueSelector(
        arg_stream=arg_stream, key_filter=cliarg_filters.RegexTrigger(key_prefix)
    )
