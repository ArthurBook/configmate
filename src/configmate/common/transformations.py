import abc
from typing import Callable, Generic, List, Optional, Type, TypeVar

from configmate.common import context

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

Callback = Callable[[context.Context, U], None]


class Transformer(abc.ABC, Generic[T, U]):
    input_type: Type[T] = object  # type: ignore
    output_type: Type[U] = object  # type: ignore

    @abc.abstractmethod
    def _apply(self, ctx: context.Context, input_: T) -> U:
        """Apply the transformation to the input
        has access to the context via `self.context`
        """
        raise NotImplementedError

    def __init__(self, *_, **__) -> None:
        super().__init__()
        self._callbacks: List[Callback[U]] = []

    def __call__(self, input_: T, ctx: Optional[context.Context] = None) -> U:
        ctx = ctx or context.Context()
        result = self._apply(ctx, input_)
        self._run_callbacks(ctx, result)
        return result

    def __or__(self, step: "Transformer[U, V]") -> "TransformationLink[T, V]":
        return TransformationLink(self, step)

    def __rshift__(self, step: "Transformer[T, U]") -> "TransformationMap[T, U]":
        return TransformationMap(self, step)

    def append_callback(self, callback: Callback[U]) -> "Transformer[T, U]":
        self._callbacks.append(callback)
        return self

    def _run_callbacks(self, ctx: context.Context, result: U) -> None:
        for callback in self._callbacks:
            callback(ctx, result)


class TransformationLink(Transformer[T, V], Generic[T, V]):
    def __init__(self, first: Transformer[T, U], second: Transformer[U, V]) -> None:
        super().__init__()
        self._first = first
        self._next = second

    def _apply(self, ctx: context.Context, input_: T) -> V:
        return self._next(self._first(input_, ctx), ctx)

    @property
    def input_type(self) -> Type[T]:
        return self._first.input_type

    @property
    def output_type(self) -> Type[V]:
        return self._next.output_type


class TransformationMap(Transformer[T, List[U]], Generic[T, U]):
    def __init__(self, *steps: Transformer[T, U]) -> None:
        super().__init__()
        if len(steps) == 0:
            raise ValueError("At least one step is required")
        self._steps = steps

    def __rshift__(self, step: Transformer[T, U]) -> "TransformationMap[T, U]":
        return TransformationMap(*self._steps, step)

    def _apply(self, ctx: context.Context, input_: T) -> List[U]:
        return [step(input_, ctx) for step in self._steps]

    @property
    def input_type(self) -> Type[T]:
        return self._steps[0].input_type

    @property
    def output_type(self) -> Type[U]:
        return self._steps[0].output_type
