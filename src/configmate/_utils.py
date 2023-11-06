import functools
import itertools
import os
import re
from typing import (
    Any,
    Callable,
    Collection,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    overload,
)

from configmate import base

T = TypeVar("T")
U = TypeVar("U")
I = TypeVar("I", bound=Iterable)


### pipe to compose functions
class Pipe(base.HasDescription, Generic[T]):
    __slots__ = ("functions",)

    def __init__(self, *functions: Callable[[T], T]) -> None:
        self.functions = functions

    def __call__(self, value: T) -> T:
        return functools.reduce(lambda acc, func: func(acc), self.functions, value)


### regex helpers
class RegexEvaluator(base.HasDescription):
    __slots__ = ("pattern",)

    def __init__(self, pattern: re.Pattern) -> None:
        self.pattern = pattern

    def __call__(self, arg: str) -> bool:
        return self.pattern.search(arg) is not None

    @classmethod
    def compile_from_prefix(cls, prefix_pattern: str) -> "RegexEvaluator":
        escaped_prefix = re.escape(prefix_pattern)
        return cls.compile(f"^{escaped_prefix}[^{escaped_prefix}]")

    @classmethod
    def compile(cls, pattern: str) -> "RegexEvaluator":
        return RegexEvaluator(re.compile(pattern))


### iterator helpers
# fmt: off
@overload
def get_nested(dictionary: base.RecursiveMapping, *keys: str) -> Any: ...
@overload
def get_nested(dictionary: base.RecursiveSequence, *keys: int) -> Any: ...
# fmt: on
def get_nested(dictionary, *keys):
    return functools.reduce(lambda d, key: d[key], keys, dictionary)


# fmt: off
@overload
def iterate_window(iterable: Iterable[T], k: Literal[1]) -> Iterable[Tuple[T]]: ...
@overload
def iterate_window(iterable: Iterable[T], k: Literal[2]) -> Iterable[Tuple[T, T]]: ...
@overload
def iterate_window(iterable: Iterable[T], k: Literal[3]) -> Iterable[Tuple[T, T, T]]: ...
# fmt: on
def iterate_window(iterable: Iterable[T], k: int) -> Iterable[Tuple[T, ...]]:
    """Iterate over a sliding window of length k over the given iterable."""
    return zip(*(itertools.islice(iterable, i, None) for i in range(k)))


def make_nested_dict(keys: Iterable[str], value: Any) -> base.RecursiveMapping:
    """Make a nested dictionary from a sequence of keys and a value."""

    def nest_dicts(_dict: Dict[str, Any], keys: Iterator[str]) -> base.RecursiveMapping:
        if (_next_key := next(keys, None)) is not None:
            _dict[_next_key] = nest_dicts({}, keys)
        else:
            _dict[last_key] = value
        return _dict

    *_keys, last_key = keys
    nest_dicts(nested_dict := {}, iter(_keys))  # type: ignore
    return nested_dict


### Common triggers
def check_if_none(object_: Any) -> bool:
    return object_ is None


def always(_: Any) -> Literal[True]:
    return True


def make_typecheck(*types: Type) -> Callable[[Any], bool]:
    return lambda object_: isinstance(object_, types)


is_string = make_typecheck(str)
is_integer = make_typecheck(int)
is_path = make_typecheck(str, os.PathLike)


def make_iterable_checker(
    iterable_type: Type[I], *allowed_types: Type[Any]
) -> Callable[[Any], bool]:
    return lambda iterable_maybe: (
        isinstance(iterable_maybe, iterable_type)
        and all(isinstance(item, allowed_types) for item in iterable_maybe)
    )


is_sequence_of_callables = make_iterable_checker(Sequence, Callable)
is_sequence_of_strings = make_iterable_checker(Sequence, str)
is_sequence_of_ints = make_iterable_checker(Sequence, int)
is_sequence_of_collections = make_iterable_checker(Sequence, Collection)
is_sequence_of_mappings = make_iterable_checker(Sequence, Mapping)
