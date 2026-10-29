from __future__ import annotations

import sys
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Literal, Protocol

import pytest

from cleek._parsers import make_parser, run as _run
from cleek._tasks import Context, task_name_from_impl

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable  # pyright: ignore[reportPrivateUsage]

collect_ignore: list[str] = []

if sys.version_info < (3, 12):
    collect_ignore.append('test_type_aliases.py')


class Run(Protocol):
    def __call__(
        self, *args: object, backend: Literal['asyncio', 'trio'] | None = ...
    ) -> Callable[[_IntrospectableCallable], None]: ...


@pytest.fixture
def run() -> Iterator[Run]:
    ctx = Context()

    def capture_args(
        *args: object,
        backend: Literal['asyncio', 'trio'] | None = None,
    ):
        def capture_impl(impl: _IntrospectableCallable):
            ctx.task(impl, backend=backend)
            name = task_name_from_impl(impl)
            ns = make_parser(ctx).parse_args(
                (name, *(str(arg) for arg in args))
            )
            _run(
                ctx.tasks[task_name_from_impl(impl)],
                ns,
            )

        return capture_impl

    yield capture_args
