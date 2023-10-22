import abc
import collections
from typing import Callable, Collection, Generic, Iterator, OrderedDict, Tuple

from configmate import interface as i


class BaseRegistry(abc.ABC, Generic[i.T, i.U]):
    __registry__: OrderedDict[i.T, i.U]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls.__registry__ = collections.OrderedDict()

    @classmethod
    def iterate_by_priority(cls) -> Iterator[Tuple[i.T, i.U]]:
        yield from reversed(cls.__registry__.items())

    @classmethod
    def register(cls, types: Collection[i.T]) -> Callable[[i.U], i.U]:
        return lambda strategy: cls.update(strategy, types) or strategy

    @classmethod
    def update(
        cls, strategy: i.U, keys: Collection[i.T], update_order: bool = False
    ) -> None:
        for key in keys:
            if update_order:
                cls.__registry__.pop(key, "")
            cls.__registry__[key] = strategy
