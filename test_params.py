from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Literal, Protocol
import pytest

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable


class SupportsName(Protocol):
    __name__: str


class Run(Protocol):
    def __call__(
        self,
        *args: object,
    ) -> Callable[['_IntrospectableCallable'], None]: ...


def run_with_args(
    *args: object,
) -> Callable[['_IntrospectableCallable'], None]:
    def run_impl_with_args(impl: '_IntrospectableCallable') -> None:
        from cleek import task
        from cleek._tasks import tasks
        from cleek._runners import run

        name = 'task'
        task(name)(impl)
        run(tasks[name], tuple(str(arg) for arg in args))

    return run_impl_with_args


@pytest.fixture
def run() -> Iterator[Run]:
    from cleek._tasks import tasks

    tasks.clear()
    yield run_with_args
    tasks.clear()


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
    from pathlib import Path

    val = (Path('/'), Path('/a'), Path('/a/b'))

    @run(*val)
    def _(*a: Path) -> None:
        assert a == val


def test_var_trio_path(run: Run) -> None:
    from trio import Path

    val = (Path('/'), Path('/a'), Path('/a/b'))

    @run(*val)
    def _(*a: Path) -> None:
        assert a == val
