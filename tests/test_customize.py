from __future__ import annotations

import pytest

from cleek._tasks import Context


def test_customize_backend() -> None:
    ctx = Context()
    asyncio_task = ctx.customize(backend='asyncio')

    @asyncio_task
    async def a() -> None:
        pass

    @asyncio_task(backend='trio')
    async def b() -> None:
        pass

    assert ctx.tasks['a'].backend == 'asyncio'
    assert ctx.tasks['b'].backend == 'trio'


def test_customize_backend_beats_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('CLEEK_BACKEND', 'trio')
    ctx = Context()

    def noop() -> None:
        pass

    _ = ctx.customize(backend='asyncio')(noop)
    assert ctx.tasks['noop'].backend == 'asyncio'


def test_customized_default_group() -> None:
    assert Context().customize(group='foo.bar').default_group == 'foo.bar'


def test_uncustomized_default_group() -> None:
    assert Context().customize().default_group is None


def test_customized_default_style() -> None:
    ctx = Context()
    assert ctx.customize(style='red').default_style == 'red'


def test_uncustomized_default_style() -> None:
    assert Context().customize().default_style is None


def test_customized_task() -> None:
    ctx = Context()
    task = ctx.customize(group='foo', style='red')

    @task
    def bar() -> None:
        pass

    task_obj = ctx.tasks['foo.bar']
    assert task_obj.group == 'foo'
    assert task_obj.style == 'red'
