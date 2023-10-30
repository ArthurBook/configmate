import abc
import collections
from typing import Any, Callable, Deque, Generic, NoReturn, Tuple, TypeVar, cast

from configmate import exceptions

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Description:
    def __get__(self, instance: "HasDescription", _: Any) -> str:
        return instance.__doc__ or ""

    def __set__(self, instance: "HasDescription", value: str) -> None:
        instance.__doc__ = value


class HasDescription(abc.ABC):
    description = Description()


class BaseSource(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def read(self) -> T:
        ...


class BaseInterpolator(HasDescription, abc.ABC):
    @abc.abstractmethod
    def interpolate(self, text: str) -> str:
        ...


class BaseParser(HasDescription, abc.ABC):
    @abc.abstractmethod
    def parse(self, configlike: str) -> Any:
        ...


class BaseValidator(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def validate(self, object_: Any) -> T:
        ...


class BaseRegistry(HasDescription, abc.ABC, Generic[T, U]):
    _registry: Deque[Tuple[Callable[[T], bool], U]]
    _sentinel = object()

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = collections.deque()

    def __getitem__(self, key: T) -> U:
        return self.get_strategy(key)

    @classmethod
    def get_strategy(cls, key: T) -> U:
        strategies = (strategy for checker, strategy in cls._registry if checker(key))
        if (first_match := next(strategies, cls._sentinel)) is cls._sentinel:
            cls.raise_missing(key)
        return cast(U, first_match)

    @classmethod
    def register(cls, trigger: Callable[[T], bool], rank: int = -1) -> Callable[[U], U]:
        return lambda strategy: cls.add(trigger, strategy, rank) or strategy

    @classmethod
    def add(cls, trigger: Callable[[T], bool], strategy: U, rank: int = -1) -> None:
        cls._registry.insert(rank, (trigger, strategy))

    @classmethod
    def raise_missing(cls, unfound_key: Any) -> NoReturn:
        raise exceptions.NoStrategyAvailable(
            f"Missing strategy for {unfound_key}, please register one."
            f"\n\tAvailable strategies: "  # TODO use describe() here
        )


class FactoryRegistry(BaseRegistry[T, Callable[[Any], V]]):
    """Holds factory methods"""
