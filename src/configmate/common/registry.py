import collections
from typing import Callable, Deque, Dict, Generic, NoReturn, Tuple, TypeVar

from configmate.common import exceptions

T_contra = TypeVar("T_contra", contravariant=True)
U = TypeVar("U")


class DictRegistryMixin(Generic[T_contra, U]):
    _registry: Dict[T_contra, U]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = {}
        return super().__init_subclass__(*args, **kwargs)

    @classmethod
    def lookup(cls, key: T_contra) -> U:
        """Retrieves first triggered strategy or raises `~exceptions.NoApplicableStrategy`."""
        if key in cls._registry:
            return cls._registry[key]
        _raise_missing(cls, key)

    @classmethod
    def register(cls, key: T_contra, value: U) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry[key] = value


class StrategyRegistryMixin(Generic[T_contra, U]):
    _registry: Deque[Tuple[Callable[[T_contra], bool], U]]

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = collections.deque()
        return super().__init_subclass__(*args, **kwargs)

    def get_first_match(self, key: T_contra) -> U:
        """Retrieves first triggered strategy or raises `~exceptions.NoApplicableStrategy`."""
        for entry in (entry for trigger, entry in self._registry if trigger(key)):
            return entry
        _raise_missing(self, key)

    @classmethod
    def register(
        cls, trigger: Callable[[T_contra], bool], entry: U, rank: int = -1
    ) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry.insert(rank, (trigger, entry))


def _raise_missing(self: object, unfound_key) -> NoReturn:
    raise exceptions.NoApplicableStrategy(
        f"Missing strategy for {unfound_key}, please register one."
        f"\n\tAvailable strategies: "  # TODO describe _registry
    )