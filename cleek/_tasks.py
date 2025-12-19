from collections.abc import Callable
from dataclasses import dataclass as _dataclass
from typing import (
    Final as _Final,
    TYPE_CHECKING,
    Protocol as _Protocol,
    final as _final,
    overload as _overload,
)

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable


class SupportsDunderName(_Protocol):
    __name__: str


@_final
@_dataclass(frozen=True)
class Task:
    impl: _Final['_IntrospectableCallable']
    name: _Final[str]
    group: _Final[str | None] = None
    style: _Final[str | None] = None

    @property
    def full_name(self) -> str:
        parts: list[str] = []
        if self.group is not None:
            parts.append(self.group)
        parts.append(self.name)
        return '.'.join(parts)


def task_name_from_impl(impl: 'SupportsDunderName') -> str:
    return impl.__name__.replace('_', '-')


@_final
class _Customize:
    def __init__(
        self,
        ctx: 'Context',
        group: str | None = None,
        *,
        style: str | None = None,
    ) -> None:
        self._ctx: _Final = ctx
        self._group: _Final = group
        self._style: _Final = style

    @_overload
    def __call__[**P, T](
        self,
        impl: Callable[P, T],
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
    ) -> Callable[P, T]: ...

    @_overload
    def __call__[**P, T](
        self,
        name: str | None = ...,
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

    def __call__[**P, T](
        self,
        implOrName: Callable[P, T] | str | None = None,
        /,
        *,
        group: str | None = None,
        style: str | None = None,
    ) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
        if group is None:
            group = self._group
        if style is None:
            style = self._style
        return self._ctx.task(implOrName, group=group, style=style)


@_final
class Context:
    def __init__(self) -> None:
        self.tasks: _Final[dict[str, Task]] = {}

    def customize(
        self,
        group: str | None = None,
        *,
        style: str | None = None,
    ) -> _Customize:
        return _Customize(self, group=group, style=style)

    @_overload
    def task[**P, T](
        self,
        impl: Callable[P, T],
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
    ) -> Callable[P, T]: ...

    @_overload
    def task[**P, T](
        self,
        name: str | None = ...,
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
    ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...

    def task[**P, T](
        self,
        implOrName: Callable[P, T] | str | None = None,
        /,
        *,
        group: str | None = None,
        style: str | None = None,
    ) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
        def register(name: str, impl: Callable[P, T]) -> Callable[P, T]:
            task = Task(impl=impl, name=name, group=group, style=style)
            full_name = task.full_name

            if full_name in self.tasks:
                raise ValueError(f'task named {full_name!r} already exists')

            self.tasks[task.full_name] = task
            return impl

        if implOrName is None:

            def unnamed_task(impl: Callable[P, T]) -> Callable[P, T]:
                return register(task_name_from_impl(impl), impl)

            return unnamed_task

        if isinstance(implOrName, str):
            name = implOrName

            def named_task(impl: Callable[P, T]) -> Callable[P, T]:
                return register(name, impl)

            return named_task

        impl = implOrName
        return register(task_name_from_impl(impl), impl)
