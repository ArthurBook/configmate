import abc
import collections
import functools
from typing import Any, Callable, Generic, NoReturn, OrderedDict, TypeVar

from configmate import exceptions

T = TypeVar("T")
U = TypeVar("U")


class ConfigMateVerbosity:
    def __call__(self) -> int:
        return 0


class HasDescription(abc.ABC):
    def describe(self, verbosity: int) -> str:
        return repr(self) if verbosity else self.short_description()

    def short_description(self) -> str:
        return ""


class BaseSource(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def read(self) -> T:
        ...


class BaseFactory(abc.ABC, Generic[T, U]):
    @abc.abstractmethod
    def __call__(self, *input_args: T) -> U:
        ...


class BaseRegistry(abc.ABC, Generic[T, U]):
    __registry__: OrderedDict[T, U]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls.__registry__ = collections.OrderedDict()

    @staticmethod
    @abc.abstractmethod
    def is_valid_strategy(type_: Any, key: T) -> bool:
        ...

    @classmethod
    def get_strategy(cls, key: Any) -> U:
        is_valid = functools.partial(cls.is_valid_strategy, key)
        valid_keys = filter(is_valid, reversed(cls.__registry__.keys()))
        try:
            return cls.__registry__[next(valid_keys)]
        except StopIteration as exc:
            cls.raise_missing(key, exc)

    @classmethod
    def register(cls, *keys: T) -> Callable[[U], U]:
        return lambda strategy: cls.update(strategy, *keys) or strategy

    @classmethod
    def update(cls, strategy: U, *keys: T, update_order: bool = False) -> None:
        _ = [cls.__registry__.pop(key, None) for key in keys if update_order]
        cls.__registry__.update({key: strategy for key in keys})

    @classmethod
    def raise_missing(cls, unfound_key: T, cause: Exception) -> NoReturn:
        raise exceptions.NoStrategyAvailable(
            f"Missing strategy for {unfound_key}, please register one."
            f"\n\tAvailable strategies: {list(cls.__registry__.keys())}"
        ) from cause
