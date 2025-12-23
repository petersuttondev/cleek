from __future__ import annotations
from collections.abc import Callable, Iterator
from inspect import signature
from pathlib import Path
from typing import Literal, Protocol, TYPE_CHECKING

import pytest
import trio

from cleek._parsers import _NO, _OptionRegistry, make_parser, run as _run
from cleek._tasks import Context, Task, task_name_from_impl

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable


def noop() -> None:  # pragma: no cover
    pass


class Run(Protocol):
    def __call__(
        self,
        *args: object,
    ) -> Callable[['_IntrospectableCallable'], None]: ...


@pytest.fixture
def run() -> Iterator[Run]:
    ctx = Context()

    def capture_args(*args: object):
        def capture_impl(impl: '_IntrospectableCallable'):
            ctx.task(impl)
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


def test_no_args(run: Run) -> None:
    @run()
    def _() -> None:
        assert True


def test_pk_bool_def_false_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: bool = False) -> None:
        assert a is True


def test_pk_bool_default_true_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: bool = True) -> None:
        assert a is False


def test_pk_opt_bool_def_none(run: Run) -> None:
    @run()
    def _(a: bool | None = None) -> None:
        assert a is None


def test_pk_opt_bool_def_none_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: bool | None = None) -> None:
        assert a is True


def test_pk_opt_bool_def_none_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: bool | None = None) -> None:
        assert a is False


def test_pk_opt_bool_def_false(run: Run) -> None:
    @run()
    def _(a: bool | None = False) -> None:
        assert a is False


def test_pk_opt_bool_def_false_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: bool | None = False) -> None:
        assert a is True


def test_pk_opt_bool_def_true(run: Run) -> None:
    @run()
    def _(a: bool | None = True) -> None:
        assert a is True


def test_pk_opt_bool_def_true_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: bool | None = True) -> None:
        assert a is False


def test_p_str(run: Run) -> None:
    val = 'b'

    @run(val)
    def _(a: str) -> None:
        assert a == val


def test_p_opt_str(run: Run) -> None:
    @run()
    def _(a: str | None) -> None:
        assert a is None


def test_p_opt_str_val(run: Run) -> None:
    val = 'b'

    @run('-a', val)
    def _(a: str | None) -> None:
        assert a == val


def test_pk_str_def_str(run: Run) -> None:
    val = 'b'

    @run()
    def _(a: str = val) -> None:
        assert a == val


def test_pk_str_def_str_arg_str(run: Run) -> None:
    val = 'c'

    @run('-a', val)
    def _(a: str = 'b') -> None:
        assert a == val


def test_pk_opt_str_def_none(run: Run) -> None:
    @run()
    def _(a: str | None = None) -> None:
        assert a is None


def test_pk_opt_str_def_none_arg_str(run: Run) -> None:
    val = 'b'

    @run('-a', val)
    def _(a: str | None = None) -> None:
        assert a == val


def test_pk_opt_str_def_str(run: Run) -> None:
    val = 'b'

    @run()
    def _(a: str | None = val) -> None:
        assert a == val


def test_pk_opt_str_def_str_arg_str(run: Run) -> None:
    val = 'c'

    @run('-a', val)
    def _(a: str | None = 'b') -> None:
        assert a == val


def test_var_str(run: Run) -> None:
    val = ('a', 'b', 'c')

    @run(*val)
    def _(*a: str) -> None:
        assert a == val


def test_p_int(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: int) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_int(run: Run) -> None:
    val = 2

    @run('-a', val)
    def _(a: int = 1) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: int = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int_def_none(run: Run) -> None:
    @run()
    def _(a: int | None = None) -> None:
        assert a is None


def test_pk_opt_int_def_none_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: int | None = None) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: int | None = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int_def_int_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: int | None = 2) -> None:
        assert isinstance(a, int)
        assert a == val


def test_p_float(run: Run) -> None:
    val = 1.0

    @run(val)
    def _(a: float) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_float_def_float(run: Run) -> None:
    val = 1.0

    @run()
    def _(a: float = val) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_float_def_float_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: float = 2.0) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_none(run: Run) -> None:
    @run()
    def _(a: float | None = None) -> None:
        assert a is None


def test_pk_opt_float_def_none_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: float | None = None) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_float(run: Run) -> None:
    val = 1.0

    @run()
    def _(a: float | None = val) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_float_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: float | None = 2.0) -> None:
        assert isinstance(a, float)
        assert a == val


def test_p_literal_int(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: Literal[1, 2, 3]) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_literal_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: Literal[1, 2, 3] = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_literal_int_def_int_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: Literal[1, 2, 3] = 2) -> None:
        assert isinstance(a, int)
        assert a == val


def test_p_literal_str(run: Run) -> None:
    val = 'a'

    @run(val)
    def _(a: Literal['a', 'b', 'c']) -> None:
        assert isinstance(a, str)
        assert a == val


def test_p_literal_str_def_str(run: Run) -> None:
    val = 'a'

    @run()
    def _(a: Literal['a', 'b', 'c'] = val) -> None:
        assert isinstance(a, str)
        assert a == val


def test_p_literal_str_def_str_arg_str(run: Run) -> None:
    val = 'a'

    @run('-a', val)
    def _(a: Literal['a', 'b', 'c'] = 'b') -> None:
        assert isinstance(a, str)
        assert a == val


def test_var_pathlib_path(run: Run) -> None:
    val = (Path('/'), Path('/a'), Path('/a/b'))

    @run(*val)
    def _(*a: Path) -> None:
        assert a == val


def test_var_trio_path(run: Run) -> None:
    val = (trio.Path('/'), trio.Path('/a'), trio.Path('/a/b'))

    @run(*val)
    def _(*a: trio.Path) -> None:
        assert a == val


def test_coro_func_impl(run: Run) -> None:
    called = False

    @run()
    async def _() -> None:
        nonlocal called
        called = True

    assert called


def test_impl_returns_coro(run: Run) -> None:
    called = False

    @run()
    def _():
        async def foo():
            nonlocal called
            called = True

        return foo()

    assert called


def test_full_name() -> None:
    name = 'bar'
    group = 'foo'
    task = Task(noop, name, group=group)
    assert task.full_name == f'{group}.{name}'


def test_check_free_raises_when_passed_reserved_short() -> None:
    from cleek._parsers import _OptionRegistry

    reg = _OptionRegistry()
    reg.reserve_short('-a')
    with pytest.raises(ValueError):
        reg.check_free('-a')


def test_check_free_raises_when_passed_reserved_long() -> None:
    from cleek._parsers import _OptionRegistry

    reg = _OptionRegistry()
    reg.reserve_long('--long')
    with pytest.raises(ValueError):
        reg.check_free('--long')


def test_find_free_short_raises_when_no_free_lower() -> None:
    from cleek._parsers import _OptionRegistry, _YES

    reg = _OptionRegistry(yes_chars='a', no_chars='A')
    reg.reserve_short('-a')
    with pytest.raises(ValueError):
        reg.find_free_short(_YES, 'a')


def test_find_free_short_raises_when_no_free_upper() -> None:
    from cleek._parsers import _OptionRegistry, _NO

    reg = _OptionRegistry(no_chars='A')
    reg.reserve_short('-A')
    with pytest.raises(ValueError):
        reg.find_free_short(_NO, 'a')


def test_find_free_long_raises_when_no_free_lower() -> None:
    from cleek._parsers import _OptionRegistry, _YES

    reg = _OptionRegistry(no_chars='A')
    dest = 'long'
    reg.reserve_long(f'--{dest}')

    with pytest.raises(ValueError):
        reg.find_free_long(_YES, dest)


def test_find_free_long_raises_when_no_free_upper() -> None:
    reg = _OptionRegistry(no_chars='A')
    dest = 'long'
    reg.reserve_long(f'--no-{dest}')

    with pytest.raises(ValueError):
        reg.find_free_long(_NO, dest)


def test_raises_unsupported_signature(run: Run) -> None:
    from cleek._parsers import UnsupportedSignature

    class Foo:
        pass

    def impl(_: 'Foo') -> None: ...

    with pytest.raises(UnsupportedSignature) as exc_info:
        run()(impl)

    assert exc_info.value.signature == signature(impl, eval_str=True)


def test_task_with_group() -> None:
    ctx = Context()

    group = 'a'

    @ctx.task(group=group)
    def impl() -> None:  # pragma: no cover
        pass

    assert ctx.tasks[f'a.{impl.__name__}'].group == group


def test_customize() -> None:
    ctx = Context()
    group = 'group'
    style = 'red'

    @ctx.customize(group=group, style=style)
    def impl() -> None:  # pragma: no cover
        pass

    task = ctx.tasks[f'{group}.{impl.__name__}']
    assert task.group == group
    assert task.style == style


def test_check_duplicate_task_name_raises() -> None:
    ctx = Context()
    name = 'a'
    ctx.task(name)(noop)

    with pytest.raises(ValueError):
        ctx.task(name)(noop)
