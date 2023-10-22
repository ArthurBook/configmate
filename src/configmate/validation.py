from typing import Any, Callable, Collection, Generic, Mapping, Sequence, Type, TypeVar

from configmate import base, exceptions
from configmate import interface as i

T = TypeVar("T")
ValidationStrategy = Callable[[Any, Type[T]], T]


class Validator(Generic[T]):
    def __init__(self, type_: Type[T]) -> None:
        super().__init__()
        self.type_ = type_

    def __call__(self, unvalidated_object: Any) -> T:
        strategy = ValidationStrategyRegistry.get_strategy(unvalidated_object)
        return strategy(unvalidated_object, self.type_)


class ValidationStrategyRegistry(base.BaseRegistry[Type[Any], ValidationStrategy]):
    @classmethod
    def get_strategy(cls, items: Sequence[Any]) -> ValidationStrategy:
        for _type, strategy in cls.iterate_by_priority():
            if isinstance(items, _type):
                return strategy
        raise exceptions.UnknownObjectType.from_objects(items)


### Implementations
@ValidationStrategyRegistry.register((Collection,))
def validate_as_unpacked_args(object_: Collection, target_type: Type[i.T]) -> i.T:
    return target_type(*object_)


@ValidationStrategyRegistry.register((Mapping,))
def validate_as_unpacked_kwargs(object_: Mapping, target_type: Type[i.T]) -> i.T:
    return target_type(**object_)
