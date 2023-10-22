from typing import Any, Collection, Mapping, Sequence, Type

from configmate import base, exceptions
from configmate import interface as i


def validate(unvalidated_object: Any, target_type: Type[i.T]) -> i.T:
    validator = ValidationStrategyRegistry.get_strategy(unvalidated_object)
    return validator(unvalidated_object, target_type)


class ValidationStrategyRegistry(base.BaseRegistry[Type, i.Validator]):
    @classmethod
    def get_strategy(cls, items: Sequence[i.T]) -> i.Validator:
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
