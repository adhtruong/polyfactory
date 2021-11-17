from random import randint
from typing import Any, Callable, List, Optional, Set, Type, Union, cast

from pydantic import ConstrainedList, ConstrainedSet

from pydantic_factories.exceptions import ParameterError


def create_constrained_of_collection(
    t_type: Any,
    collection_type: Union[Type[list], Type[set]],
    providers: dict[Any, Callable],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> Union[list, set]:
    """Generate a constrained list or set"""
    if min_items is None:
        min_items = 0
    if max_items is None:
        max_items = min_items + 1
    assert max_items >= min_items, "max_items must be longer or equal to min_items"
    if t_type is Any:
        t_type = str
    collection: Union[list, set] = collection_type()
    while len(collection) < randint(min_items, max_items):
        handler = providers[t_type]
        if handler:
            value = handler()
            assert value is not None, f"cannot generate a constrained {t_type.__name__} of ${t_type.__name__} elements"
            if isinstance(collection, set):
                collection.add(value)
            else:
                collection.append(value)
    return collection


def handle_constrained_set(field: ConstrainedSet, providers: dict[Any, Callable]) -> Set[Any]:
    """Handle ConstrainedSet instances"""
    try:
        return cast(
            Set,
            create_constrained_of_collection(
                t_type=field.item_type,
                collection_type=set,
                min_items=field.min_items,
                max_items=field.max_items,
                providers=providers,
            ),
        )
    except TypeError as e:
        raise ParameterError(f"cannot generate a constrained set of an hashable type: {field.item_type}") from e


def handle_constrained_list(field: ConstrainedList, providers: dict[Any, Callable]) -> List[Any]:
    """Handle ConstrainedList instances"""
    return cast(
        List,
        create_constrained_of_collection(
            t_type=field.item_type,
            collection_type=list,
            min_items=field.min_items,
            max_items=field.max_items,
            providers=providers,
        ),
    )
