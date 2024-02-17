import collections
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Generic,
    Literal,
    NoReturn,
    Tuple,
    TypeVar,
)

from configmate.base import exceptions, types

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)


class DictRegistryMixin(types.HasDescription, Generic[T_contra, T]):
    _registry: Dict[T_contra, T]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry: Dict[T_contra, T] = {}
        return super().__init_subclass__(*args, **kwargs)

    @classmethod
    def lookup(cls, key: T_contra) -> T:
        """Retrieves first triggered strategy or raises `~exceptions.NoApplicableStrategy`."""
        if key in cls._registry:
            return cls._registry[key]
        _raise_missing(cls, key)

    @classmethod
    def register(cls, key: T_contra, value: T) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry[key] = value

    @classmethod
    def describe(cls) -> str:
        """Returns a string representation of all items in the registry."""
        return "\n".join(f"{key}: {value}" for key, value in cls._registry.items())


class StrategyRegistryMixin(types.HasDescription, Generic[T_contra, T]):
    _registry: Deque[Tuple[Callable[[T_contra], bool], T]]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = collections.deque()
        return super().__init_subclass__(*args, **kwargs)

    @classmethod
    def get_first_match(cls, key: T_contra) -> T:
        """Retrieves first triggered strategy or raises `~exceptions.NoApplicableStrategy`."""
        for entry in (entry for trigger, entry in cls._registry if trigger(key)):
            return entry
        _raise_missing(cls, key)

    @classmethod
    def register(
        cls,
        trigger: Callable[[T_contra], bool],
        entry: T,
        where: Literal["first", "last"] = "last",
    ) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        if where == "first":
            cls._registry.appendleft((trigger, entry))
        elif where == "last":
            cls._registry.append((trigger, entry))
        else:
            raise ValueError(f"Invalid rank: {where}")

    @classmethod
    def describe(cls) -> str:
        """Returns a string representation of all items in the registry."""
        return "\n".join(
            f"{entry[1]} (triggered by: {entry[0].__name__})" for entry in cls._registry
        )


def _raise_missing(cls: types.HasDescription, unfound_key: Any) -> NoReturn:
    raise exceptions.NoApplicableStrategy(
        f"Missing strategy for {unfound_key}, please register one."
        f"\n\tAvailable strategies:\n{cls.describe()}"
    )
