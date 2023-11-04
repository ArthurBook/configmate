import functools
from typing import (
    Any,
    Callable,
    Generic,
    Literal,
    Mapping,
    Sequence,
    Type,
    TypeVar,
    overload,
)

T = TypeVar("T")
U = TypeVar("U")

RecursiveMapping = Mapping[str, "RecursiveMapping"]
RecursiveSequence = Sequence["RecursiveSequence"]


### pipe to compose functions
class Pipe(Generic[T]):
    def __init__(self, *functions: Callable[[T], T]) -> None:
        self.functions = functions

    def __call__(self, value: T) -> T:
        return functools.reduce(lambda acc, func: func(acc), self.functions, value)


### helpers
# fmt: off
@overload
def get_nested(dictionary: RecursiveMapping, *keys: str) -> Any: ...
@overload
def get_nested(dictionary: RecursiveSequence, *keys: int) -> Any: ...
# fmt: on
def get_nested(dictionary, *keys):
    return functools.reduce(lambda d, key: d[key], keys, dictionary)


### Common triggers
def make_typecheck(*types: Type) -> Callable[[Any], bool]:
    return lambda object_: isinstance(object_, types)


def check_if_callable(object_: Any) -> bool:
    return callable(object_)


def check_if_none(object_: Any) -> bool:
    return object_ is None


def check_if_callable_sequence(sequence_maybe: Any) -> bool:
    return isinstance(sequence_maybe, Sequence) and all(map(callable, sequence_maybe))


def always(_: Any) -> Literal[True]:
    return True
