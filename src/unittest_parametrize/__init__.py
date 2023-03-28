from __future__ import annotations

import inspect
import sys
from functools import wraps
from types import FunctionType
from typing import Any
from typing import Callable
from typing import overload
from typing import Sequence
from typing import TypeVar
from unittest import TestCase

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


class ParametrizedTestCase(TestCase):
    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        for name, func in list(cls.__dict__.items()):
            if not isinstance(func, FunctionType):
                continue
            if not hasattr(func, "_parametrized"):
                continue

            # TODO: check through decorator chain, if there's a decorator above
            # @parametrize, error

            _parametrized = func._parametrized  # type: ignore [attr-defined]
            delattr(cls, name)
            for param in _parametrized.params:
                params = dict(zip(_parametrized.argnames, param.args))

                @wraps(func)
                def test(
                    self: TestCase,
                    *args: Any,
                    _func: FunctionType = func,
                    _params: dict[str, Any] = params,
                    **kwargs: Any,
                ) -> Any:
                    return _func(self, *args, **_params, **kwargs)

                test.__name__ = f"{name}_{param.id}"
                test.__qualname__ = f"{test.__qualname__}_{param.id}"

                setattr(cls, test.__name__, test)


class param:
    __slots__ = ("args", "id")

    def __init__(self, *args: Any, id: str) -> None:
        self.args = args
        # TODO: escape id as ASCII as per pytest
        self.id = id


class parametrized:
    def __init__(self, argnames: Sequence[str], params: Sequence[param]) -> None:
        self.argnames = argnames
        self.params = params


P = ParamSpec("P")
T = TypeVar("T")
TestFunc = Callable[P, T]


@overload
def parametrize(
    argnames: Sequence[str],
    argvalues: Sequence[tuple[Any, ...]],
    ids: Sequence[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:  # pragma: no cover
    ...


@overload
def parametrize(
    argnames: Sequence[str],
    argvalues: Sequence[param],
    ids: None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:  # pragma: no cover
    ...


def parametrize(
    argnames: Sequence[str],
    argvalues: Sequence[tuple[Any, ...]] | Sequence[param],
    ids: Sequence[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    # TODO support comma-separated string for argnames

    if len(argnames) == 0:
        raise ValueError("argnames must contain at least one element")

    if ids is not None and len(ids) != len(argvalues):
        raise ValueError("ids must have the same length as argvalues")

    params = []
    for i, argvalue in enumerate(argvalues):
        if isinstance(argvalue, tuple):
            if len(argvalue) != len(argnames):
                raise ValueError(
                    f"tuple at index {i} has wrong number of arguments "
                    + f"({len(argvalue)} != {len(argnames)})"
                )
            if ids:
                id_ = ids[i]
            else:
                id_ = str(i)
            params.append(param(*argvalue, id=id_))
        elif isinstance(argvalue, param):
            if len(argvalue.args) != len(argnames):
                raise ValueError(
                    f"param at index {i} has wrong number of arguments "
                    + f"({len(argvalue.args)} != {len(argnames)})"
                )
            params.append(argvalue)

        else:
            raise TypeError(
                f"argvalue at index {i} is not a tuple or param instance: {argvalue!r}"
            )

    _parametrized = parametrized(argnames, params)
    bind_kwargs = {k: None for k in _parametrized.argnames}

    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        # Check given argnames will work
        sig = inspect.signature(func)
        sig.bind_partial(**bind_kwargs)

        func._parametrized = _parametrized  # type: ignore [attr-defined]
        return func

    return wrapper
