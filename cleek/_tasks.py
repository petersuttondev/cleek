from __future__ import annotations

import os as _os
from dataclasses import dataclass as _dataclass
from typing import (
    TYPE_CHECKING,
    Final as _Final,
    Literal as _Literal,
    ParamSpec as _ParamSpec,
    Protocol as _Protocol,
    TypeVar as _TypeVar,
    final as _final,
    overload as _overload,
)

if TYPE_CHECKING:
    from collections.abc import Callable as _Callable
    from inspect import _IntrospectableCallable  # pyright: ignore[reportPrivateUsage]

    class SupportsDunderName(_Protocol):
        __name__: str


def _get_default_backend() -> _Literal['asyncio', 'trio']:
    key = 'CLEEK_BACKEND'
    match _os.environ.get(key):
        case 'asyncio' | 'trio' as backend:
            return backend
        case '' | None:
            return 'trio'
        case _ as invalid:
            raise ValueError(
                f'{key!r} set to invalid backend {invalid!r}. Should be asyncio or trio.'
            )


@_final
@_dataclass(frozen=True)
class Task:
    impl: _Final['_IntrospectableCallable']
    name: _Final[str]
    group: _Final[str | None] = None
    style: _Final[str | None] = None
    backend: _Final[_Literal['asyncio', 'trio']] = 'trio'

    @property
    def full_name(self) -> str:
        parts: list[str] = []
        if self.group is not None:
            parts.append(self.group)
        parts.append(self.name)
        return '.'.join(parts)


def task_name_from_impl(impl: 'SupportsDunderName') -> str:
    return impl.__name__.replace('_', '-')


_T = _TypeVar('_T')
_P = _ParamSpec('_P')


@_final
class _Customize:
    def __init__(
        self,
        ctx: 'Context',
        group: str | None = None,
        *,
        style: str | None = None,
        backend: _Literal['asyncio', 'trio'] | None = None,
    ) -> None:
        self._ctx: _Final = ctx
        self._group: _Final = group
        self._style: _Final = style
        self._backend: _Final = backend

    @_overload
    def __call__(
        self,
        impl: _Callable[_P, _T],
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
        backend: _Literal['asyncio', 'trio'] | None = ...,
    ) -> _Callable[_P, _T]: ...

    @_overload
    def __call__(
        self,
        name: str | None = ...,
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
        backend: _Literal['asyncio', 'trio'] | None = ...,
    ) -> _Callable[[_Callable[_P, _T]], _Callable[_P, _T]]: ...

    def __call__(
        self,
        implOrName: _Callable[_P, _T] | str | None = None,
        /,
        *,
        group: str | None = None,
        style: str | None = None,
        backend: _Literal['asyncio', 'trio'] | None = None,
    ) -> _Callable[_P, _T] | _Callable[[_Callable[_P, _T]], _Callable[_P, _T]]:
        if group is None:
            group = self._group
        if style is None:
            style = self._style
        if backend is None:
            backend = self._backend
        return self._ctx.task(
            implOrName,
            group=group,
            style=style,
            backend=backend,
        )


@_final
class Context:
    def __init__(self) -> None:
        self.tasks: _Final[dict[str, Task]] = {}
        self.prepend_to_path = False

    def config(self, *, prepend_to_path: bool | None = None) -> None:
        if prepend_to_path is not None:
            self.prepend_to_path = prepend_to_path

    def customize(
        self,
        group: str | None = None,
        *,
        style: str | None = None,
        backend: _Literal['asyncio', 'trio'] | None = None,
    ) -> _Customize:
        return _Customize(self, group=group, style=style, backend=backend)

    @_overload
    def task(
        self,
        impl: _Callable[_P, _T],
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
        backend: _Literal['asyncio', 'trio'] | None = ...,
    ) -> _Callable[_P, _T]: ...

    @_overload
    def task(
        self,
        name: str | None = ...,
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
        backend: _Literal['asyncio', 'trio'] | None = ...,
    ) -> _Callable[[_Callable[_P, _T]], _Callable[_P, _T]]: ...

    def task(
        self,
        impl_or_name: _Callable[_P, _T] | str | None = None,
        /,
        *,
        group: str | None = None,
        style: str | None = None,
        backend: _Literal['asyncio', 'trio'] | None = None,
    ) -> _Callable[_P, _T] | _Callable[[_Callable[_P, _T]], _Callable[_P, _T]]:
        def register(name: str, impl: _Callable[_P, _T]) -> _Callable[_P, _T]:
            task = Task(
                impl=impl,
                name=name,
                group=group,
                style=style,
                backend=backend or _get_default_backend(),
            )

            full_name = task.full_name

            if full_name in self.tasks:
                raise ValueError(f'task named {full_name!r} already exists')

            self.tasks[task.full_name] = task
            return impl

        if impl_or_name is None:

            def unnamed_task(impl: _Callable[_P, _T]) -> _Callable[_P, _T]:
                return register(task_name_from_impl(impl), impl)

            return unnamed_task

        if isinstance(impl_or_name, str):
            name = impl_or_name

            def named_task(impl: _Callable[_P, _T]) -> _Callable[_P, _T]:
                return register(name, impl)

            return named_task

        impl = impl_or_name
        return register(task_name_from_impl(impl), impl)
