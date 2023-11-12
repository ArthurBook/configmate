import collections
import functools
import os
import re
from typing import (
    Any,
    Callable,
    Collection,
    Deque,
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
class RegexTrigger(base.HasDescription):
    __slots__ = ("pattern",)

    def __init__(self, pattern: re.Pattern) -> None:
        self.pattern = pattern

    def __call__(self, arg: str) -> bool:
        return self.pattern.search(arg) is not None

    @classmethod
    def compile_from_prefix(cls, prefix_pattern: str) -> "RegexTrigger":
        escaped_prefix = re.escape(prefix_pattern)
        return cls.compile(f"^{escaped_prefix}[^{escaped_prefix}]")

    @classmethod
    def compile(cls, pattern: str) -> "RegexTrigger":
        return RegexTrigger(re.compile(pattern))


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
# pylint: disable=line-too-long
@overload
def iterate_window(iterable: Iterable[T], size: Literal[1], step: int = 1) -> Iterator[Tuple[T,...]]:
    """Iterate with a sliding window of length `size` in steps of size `step`."""
@overload
def iterate_window(iterable: Iterable[T], size: Literal[1], step: int = 1) -> Iterator[Tuple[T]]:...
@overload
def iterate_window(iterable: Iterable[T], size: Literal[2], step: int = 1) -> Iterator[Tuple[T,T]]:...
@overload
def iterate_window(iterable: Iterable[T], size: Literal[3], step: int = 1) -> Iterator[Tuple[T,T,T]]:...
def iterate_window(iterable: Iterable[T], size, step=1)-> Iterator[Tuple[T,...]]:
    # fmt: on
    # pylint: enable=line-too-long
    sliding_window: Deque[T] = collections.deque(maxlen=size)
    _step = 0
    for item in iterable:
        sliding_window.append(item)
        if len(sliding_window) == size:
            if _step % step == 0:
                yield tuple(sliding_window)
            _step += 1
 

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
def is_none(object_: Any) -> bool:
    return object_ is None


def always(_: Any) -> Literal[True]:
    return True


def make_typecheck(*types: Type) -> Callable[[Any], bool]:
    return lambda object_: isinstance(object_, types)


is_string = make_typecheck(str)
is_integer = make_typecheck(int)
is_dict = make_typecheck(dict)
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
