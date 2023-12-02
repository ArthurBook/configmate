import collections
from typing import Callable, Deque, Dict, Generic, NoReturn, Tuple, TypeVar

from configmate.base import exceptions

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)


class DictRegistryMixin(Generic[T_contra, T]):
    _registry: Dict[T_contra, T]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = {}
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


class StrategyRegistryMixin(Generic[T_contra, T]):
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
        cls, trigger: Callable[[T_contra], bool], entry: T, rank: int = -1
    ) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry.insert(rank, (trigger, entry))


def _raise_missing(self: object, unfound_key) -> NoReturn:
    raise exceptions.NoApplicableStrategy(
        f"Missing strategy for {unfound_key}, please register one."
        f"\n\tAvailable strategies: "  # TODO describe _registry
    )
