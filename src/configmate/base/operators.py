import abc
import collections
import copy
import itertools
import types
from typing import (
    Callable,
    DefaultDict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    overload,
)

T = TypeVar("T")
U = TypeVar("U")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class Context:
    "Holds the context for the configmate pipeline."
    _namespaces: DefaultDict[int, types.SimpleNamespace]
    _children: List["Context"]

    def __init__(self) -> None:
        self._namespaces = collections.defaultdict(types.SimpleNamespace)
        self._children = []

    def __getitem__(self, key: object) -> types.SimpleNamespace:
        return self._namespaces[id(key)]

    def __copy__(self) -> "Context":
        new = Context()
        new._namespaces = copy.copy(self._namespaces)
        return new

    def get_child(self) -> "Context":
        child = copy.copy(self)
        self._children.append(child)
        return child


Callback = Callable[[Context, T_contra], None]


class Operator(abc.ABC, Generic[T_contra, T_co]):
    input_type: Type[T_contra] = object  # type: ignore
    output_type: Type[T_co] = object  # type: ignore

    @abc.abstractmethod
    def _transform(self, ctx: Context, input_: T_contra) -> T_co:
        """Apply the transformation to the input
        has access to the context via `self.context`
        """

    def __init__(self, *_, **__) -> None:
        super().__init__()
        self._callbacks: List[Callback[T_co]] = []

    def __call__(self, input_: T_contra, _ctx: Optional[Context] = None) -> T_co:
        _ctx = Context() if _ctx is None else _ctx
        result = self._transform(_ctx, input_)
        self._run_callbacks(_ctx, result)
        return result

    @overload
    def pipe_to(self, step: None) -> "Operator[T_contra, T_co]": ...
    @overload
    def pipe_to(self, step: "Operator[T_co, T]") -> "Pipeline[T_contra, T]": ...
    def pipe_to(self, step: "Optional[Operator]") -> "Operator":
        return self if step is None else Pipeline(self, step)

    def append_callback(self, callback: Callback[T_co]) -> "Operator[T_contra, T_co]":
        self._callbacks.append(callback)
        return self

    def _run_callbacks(self, ctx: Context, result) -> None:
        for callback in self._callbacks:
            callback(ctx, result)


class Pipeline(Operator[T_contra, T_co]):
    """A pipeline of operators that are applied in sequence."""

    def __init__(self, first: Operator[T_contra, T], second: Operator[T, T_co]) -> None:
        super().__init__()
        self._first = first
        self._next = second

    def _transform(self, ctx: Context, input_: T_contra) -> T_co:
        return self._next(self._first(input_, ctx), ctx)

    @property
    def input_type(self) -> Type[T_contra]:  # type: ignore
        return self._first.input_type

    @property
    def output_type(self) -> Type[T_co]:  # type: ignore
        return self._next.output_type


class MapIterable(Operator[Iterable[T_contra], Iterator[T_co]]):
    """Maps an ~Operator over an iterable."""

    input_type = Iterable  # type: ignore
    output_type = Iterator  # type: ignore

    def __init__(self, map_step: Operator[T_contra, T_co]) -> None:
        super().__init__()
        self._map_step = map_step

    def _transform(self, ctx: Context, input_: Iterable[T_contra]) -> Iterator[T_co]:
        return (self._map_step(i, ctx.get_child()) for i in input_)


class JoinOutputs(Operator[T_contra, Iterator[T_co]]):
    """Joins the outputs of multiple operators into a single iterable."""

    output_type = Iterator  # type: ignore

    def __init__(self, *steps: Operator[T_contra, T_co]) -> None:
        super().__init__()
        self._steps = steps

    def _transform(self, ctx: Context, input_: T_contra) -> Iterator[T_co]:
        return (step(input_, ctx.get_child()) for step in self._steps)


class ChainOutputs(Operator[T_contra, Iterator[T_co]]):
    """Chains multiple operators together."""

    output_type = Iterator  # type: ignore

    def __init__(self, steps: Operator[T_contra, Iterable[Iterable[T_co]]]) -> None:
        super().__init__()
        self._steps = steps

    def _transform(self, ctx: Context, input_: T_contra) -> Iterator[T_co]:
        return itertools.chain.from_iterable(self._steps(input_, ctx))
