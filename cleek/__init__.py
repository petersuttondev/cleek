from collections.abc import Callable
from typing import Final, Protocol, overload

from cleek._tasks import Task as _Task

_tasks: Final[dict[str, _Task]] = {}


@overload
def task[**P, T](
    impl: Callable[P, T],
    /,
    *,
    group: str | None = ...,
    style: str | None = ...,
) -> Callable[P, T]: ...


@overload
def task[**P, T](
    name: str | None = ...,
    /,
    *,
    group: str | None = ...,
    style: str | None = ...,
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


class _SupportsName(Protocol):
    __name__: str


def _name_from_impl(impl: _SupportsName) -> str:
    return impl.__name__.replace('_', '-')


def task[**P, T](
    implOrName: Callable[P, T] | str | None = None,
    /,
    *,
    group: str | None = None,
    style: str | None = None,
) -> Callable[P, T] | Callable[[Callable[P, T]], Callable[P, T]]:
    def register(name: str, impl: Callable[P, T]) -> Callable[P, T]:
        task = _Task(impl=impl, name=name, group=group, style=style)
        full_name = task.full_name

        if full_name in _tasks:
                raise ValueError(f'task named {full_name!r} already exists')

        _tasks[task.full_name] = task
        return impl

    if implOrName is None:

        def unnamed_task(impl: Callable[P, T]) -> Callable[P, T]:
            return register(_name_from_impl(impl), impl)

        return unnamed_task

    if isinstance(implOrName, str):
        name = implOrName

        def named_task(impl: Callable[P, T]) -> Callable[P, T]:
            return register(name, impl)

        return named_task

    impl = implOrName
    return register(_name_from_impl(impl), impl)


class customize:
    def __init__(
        self,
        group: str | None = None,
        style: str | None = None,
    ) -> None:
        self._group = group
        self._style = style

    @overload
    def __call__[**P, T](
        self,
        impl: Callable[P, T],
        /,
        *,
        group: str | None = ...,
        style: str | None = ...,
    ) -> Callable[P, T]: ...

    @overload
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
        return task(implOrName, group=group, style=style)
