import abc
import collections
from typing import (
    Any,
    Callable,
    Deque,
    Generic,
    NamedTuple,
    NoReturn,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

from configmate import exceptions

T = TypeVar("T")
U = TypeVar("U")
ClassOrCallable = Union[Type[T], Callable[..., T]]


class Description:
    def __get__(self, instance: "HasDescription", _: Any) -> str:
        return instance.__doc__ or ""

    def __set__(self, instance: "HasDescription", value: str) -> None:
        instance.__doc__ = value


class HasDescription(abc.ABC):
    description = Description()


### Key components
class BaseSource(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def read(self) -> T:
        ...


class BaseInterpolator(HasDescription, abc.ABC):
    @abc.abstractmethod
    def interpolate(self, text: str) -> str:
        ...


class BaseParser(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def parse(self, configlike: str) -> T:
        ...


class BaseAggregator(HasDescription, abc.ABC):
    @abc.abstractmethod
    def aggregate(self, sequence: Sequence[T]) -> T:
        ...


class BaseSectionSelector(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def select(self, config: T) -> Any:
        ...

    def get_not_found_exc(self, obj: Any, section: Any) -> NoReturn:
        raise exceptions.SectionNotFound(f"{section=} not found in {obj}")


class BaseValidator(HasDescription, abc.ABC, Generic[T]):
    @abc.abstractmethod
    def validate(self, object_: Any) -> T:
        ...


### MethodStore
class MethodWithTrigger(NamedTuple, Generic[T, U]):
    trigger: Callable[[T], bool]
    method: ClassOrCallable[U]


class BaseMethodStore(HasDescription, abc.ABC, Generic[T, U]):
    """A registry for strategies that are associated with a trigger function.

    The trigger function is a callable that takes a key and returns a boolean.
    The first strategy that is associated with a trigger function that returns
    a truthy value is returned by `get_strategy`. If no strategy is associated
    with a trigger function that returns a truthy value, a `NoStrategyAvailable`
    exception is raised.
    """

    _registry: Deque[MethodWithTrigger[T, U]]
    _sentinel = object()  # trigger for no applicable strategy

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = collections.deque()

    @classmethod
    def get_strategy(cls, key: T) -> ClassOrCallable[U]:
        """Retrieves first triggered strategy or raises `NoStrategyAvailable`."""
        methods = (method.method for method in cls._registry if method.trigger(key))
        if (first_match := next(methods, cls._sentinel)) is cls._sentinel:
            cls.raise_missing(key)
        return cast(ClassOrCallable[U], first_match)

    @classmethod
    def register(
        cls, trigger: Callable[[T], bool], rank: int = -1
    ) -> Callable[[ClassOrCallable[U]], ClassOrCallable[U]]:
        """Registers a new strategy and associates it with a trigger function."""

        def add_and_return(strategy: ClassOrCallable[U]) -> ClassOrCallable[U]:
            cls.add(MethodWithTrigger(trigger, strategy), rank)
            return strategy

        return add_and_return

    @classmethod
    def add(cls, method_with_trigger: MethodWithTrigger[T, U], rank: int = -1) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry.insert(rank, method_with_trigger)

    @classmethod
    def raise_missing(cls, unfound_key: Any) -> NoReturn:
        raise exceptions.NoStrategyAvailable(
            f"Missing strategy for {unfound_key}, please register one."
            f"\n\tAvailable strategies: "  # TODO describe _registry
        )
