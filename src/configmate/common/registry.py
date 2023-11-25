import collections
from typing import Callable, Deque, Generic, NoReturn, Tuple, TypeVar

from configmate.common import exceptions, types

T_contra = TypeVar("T_contra", contravariant=True)
U = TypeVar("U")


class StrategyRegistryMixin(Generic[T_contra, U]):
    _registry: Deque[Tuple[Callable[[T_contra], bool], U]]
    _sentinel = types.Sentinel()  # trigger for no applicable strategy

    def __init_subclass__(cls, *args, **kwargs) -> None:
        cls._registry = collections.deque()
        return super().__init_subclass__(*args, **kwargs)

    def get_first_match(self, key: T_contra) -> U:
        """Retrieves first triggered strategy or raises `~exceptions.NoApplicableStrategy`."""
        methods = (entry for trigger, entry in self._registry if trigger(key))
        if isinstance(first_match := next(methods, self._sentinel), types.Sentinel):
            self._raise_missing(key)
        return first_match

    @classmethod
    def register(
        cls, trigger: Callable[[T_contra], bool], entry: U, rank: int = -1
    ) -> None:
        """Inserts a new strategy at the given rank (position in queue)."""
        cls._registry.insert(rank, (trigger, entry))

    def _raise_missing(self, unfound_key: T_contra) -> NoReturn:
        raise exceptions.NoApplicableStrategy(
            f"Missing strategy for {unfound_key}, please register one."
            f"\n\tAvailable strategies: "  # TODO describe _registry
        )
