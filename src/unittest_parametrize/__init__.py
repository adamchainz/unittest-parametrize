from __future__ import annotations

import inspect
import sys
from collections.abc import Sequence
from functools import wraps
from types import FunctionType
from typing import Any, Callable, TypeVar
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

            if hasattr(func, "__wrapped__") and hasattr(
                func.__wrapped__, "_parametrized"
            ):
                raise TypeError(
                    "@parametrize must be the top-most decorator on "
                    + func.__qualname__
                )

            _parametrized = func._parametrized  # type: ignore [attr-defined]
            delattr(cls, name)
            for param in _parametrized.params:
                params = dict(zip(_parametrized.argnames, param.args))

                if inspect.iscoroutinefunction(func):

                    @wraps(func)
                    async def test(
                        self: TestCase,
                        *args: Any,
                        _func: FunctionType = func,
                        _params: dict[str, Any] = params,
                        **kwargs: Any,
                    ) -> Any:
                        try:
                            return await _func(self, *args, **_params, **kwargs)
                        except Exception as exc:
                            if sys.version_info >= (3, 11):
                                exc.add_note(
                                    "Test parameters: "
                                    + ", ".join(
                                        f"{k}={v!r}" for k, v in _params.items()
                                    )
                                )
                            raise

                else:

                    @wraps(func)
                    def test(
                        self: TestCase,
                        *args: Any,
                        _func: FunctionType = func,
                        _params: dict[str, Any] = params,
                        **kwargs: Any,
                    ) -> Any:
                        try:
                            return _func(self, *args, **_params, **kwargs)
                        except Exception as exc:
                            if sys.version_info >= (3, 11):
                                exc.add_note(
                                    "Test parameters: "
                                    + ", ".join(
                                        f"{k}={v!r}" for k, v in _params.items()
                                    )
                                )
                            raise

                test.__name__ = f"{name}_{param.id}"
                test.__qualname__ = f"{test.__qualname__}_{param.id}"

                if hasattr(cls, test.__name__):
                    raise ValueError(
                        f"Duplicate test name {test.__name__} in {cls.__name__}"
                    )

                setattr(cls, test.__name__, test)


class param:
    __slots__ = ("args", "id")

    def __init__(self, *args: Any, id: str | None = None) -> None:
        self.args = args

        if id is not None and not f"_{id}".isidentifier():
            raise ValueError(f"id must be a valid Python identifier suffix: {id!r}")

        self.id = id


class parametrized:
    __slots__ = ("argnames", "params")

    def __init__(self, argnames: Sequence[str], params: Sequence[param]) -> None:
        self.argnames = argnames
        self.params = params


P = ParamSpec("P")
T = TypeVar("T")
TestFunc = Callable[P, T]


def parametrize(
    argnames: str | Sequence[str],
    argvalues: Sequence[tuple[Any, ...] | param | Any],
    ids: Sequence[str | None] | Callable[[Any], str | None] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    if isinstance(argnames, str):
        argnames = [a.strip() for a in argnames.split(",")]

    if len(argnames) == 0:
        raise ValueError("argnames must contain at least one element")

    ids_callable = callable(ids)
    if ids is not None and not ids_callable and len(ids) != len(argvalues):  # type: ignore[arg-type]
        raise ValueError("ids must have the same length as argvalues")

    seen_ids = set()
    params = []
    for i, argvalue in enumerate(argvalues):
        if isinstance(argvalue, tuple):
            if len(argvalue) != len(argnames):
                raise ValueError(
                    f"tuple at index {i} has wrong number of arguments "
                    + f"({len(argvalue)} != {len(argnames)})"
                )
            argvalue = param(*argvalue, id=make_id(i, argvalue, ids))
            params.append(argvalue)
            seen_ids.add(argvalue.id)
        elif isinstance(argvalue, param):
            if len(argvalue.args) != len(argnames):
                raise ValueError(
                    f"param at index {i} has wrong number of arguments "
                    + f"({len(argvalue.args)} != {len(argnames)})"
                )

            if argvalue.id is None:
                argvalue = param(*argvalue.args, id=make_id(i, argvalue, ids))
            if argvalue.id in seen_ids:
                raise ValueError(f"Duplicate param id {argvalue.id!r}")
            seen_ids.add(argvalue.id)
            params.append(argvalue)
        elif len(argnames) == 1:
            argvalue = param(argvalue, id=make_id(i, (argvalue,), ids))
            seen_ids.add(argvalue.id)
            params.append(argvalue)
        else:
            raise TypeError(
                f"argvalue at index {i} is not a tuple, param instance, or single value: {argvalue!r}"
            )

    _parametrized = parametrized(argnames, params)
    bind_kwargs = dict.fromkeys(_parametrized.argnames)

    def wrapper(func: Callable[P, T]) -> Callable[P, T]:
        # Check given argnames will work
        sig = inspect.signature(func)
        sig.bind_partial(**bind_kwargs)

        if hasattr(func, "_parametrized"):
            raise TypeError(f"@parametrize cannot be stacked on {func.__qualname__}")

        func._parametrized = _parametrized  # type: ignore [attr-defined]
        return func

    return wrapper


def make_id(
    i: int,
    argvalue: tuple[Any, ...] | param,
    ids: Sequence[str | None] | Callable[[Any], str | None] | None,
) -> str:
    if callable(ids):
        if isinstance(argvalue, tuple):
            values = argvalue
        else:
            values = argvalue.args

        id_parts = []
        for value in values:
            id_part = ids(value)
            if id_part is not None:
                id_parts.append(id_part)
            else:
                id_parts.append(str(value))
        id_ = "_".join(id_parts)
        # Validate the generated ID
        if not f"_{id_}".isidentifier():
            raise ValueError(
                f"callable ids returned invalid Python identifier suffix: {id_!r}"
            )
        return id_
    elif ids and ids[i]:
        return str(ids[i])
    else:
        return str(i)
