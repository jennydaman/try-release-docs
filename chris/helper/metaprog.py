"""
Metaprogramming helper functions.
"""
import abc
import collections.abc
import typing
from typing import Type, Callable, TypeVar, ForwardRef, Optional, AsyncIterator

import typing_inspect

_T = TypeVar("_T")


def get_return_hint(fn: Callable[[...], _T]) -> Type[_T]:
    hints = typing.get_type_hints(fn)
    if "return" not in hints:
        raise ValueError(f"Function {fn} must define a return type hint.")
    return hints["return"]


def get_return_item_type(fn: Callable[[...], AsyncIterator[_T]]) -> Type[_T]:
    t = get_return_hint(fn)
    if not _is_async_iterator(t):
        raise TypeError(t)
    args = typing.get_args(t)
    if len(args) != 1:
        raise TypeError(t)
    return args[0]


def _is_async_iterator(t: Type) -> typing.TypeGuard[AsyncIterator]:
    origin = typing.get_origin(t)
    return origin is typing.AsyncIterator or origin is collections.abc.AsyncIterator


def generic_of(c: Type, t: Type[_T], is_subclass=False) -> Optional[Type[_T]]:
    """
    Get the actual class represented by a bound TypeVar of a generic.
    """
    for generic_type in typing_inspect.get_args(c):
        if isinstance(generic_type, (str, ForwardRef, TypeVar)):
            continue
        if issubclass(generic_type, t):
            return generic_type

    if hasattr(c, "__orig_bases__"):
        for subclass in c.__orig_bases__:
            if subclass is abc.ABC:
                return None
            subclass_generic = generic_of(subclass, t, is_subclass=True)
            if subclass_generic is not None:
                return subclass_generic
    if not is_subclass:
        raise TypeError(
            f"No generic of {t} found in {c} nor its subclasses."
            "\nWARNING: generic_of fails if importlib.reload was called "
            "to reload the generic type's superclass. This happens "
            "when running pdoc as a webserver."
        )
    return None
