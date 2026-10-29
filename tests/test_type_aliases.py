from __future__ import annotations

from inspect import signature
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Literal

import pytest
import trio

from cleek._parsers import UnsupportedSignature

if TYPE_CHECKING:
    from conftest import Run  # pyright: ignore[reportImplicitRelativeImport]

type _BoolAlias = bool


def test_pk_bool_def_false_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: _BoolAlias = False) -> None:
        assert a is True


def test_pk_bool_default_true_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: _BoolAlias = True) -> None:
        assert a is False


def test_pk_opt_bool_def_none(run: Run) -> None:
    @run()
    def _(a: _BoolAlias | None = None) -> None:
        assert a is None


def test_pk_opt_bool_def_none_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: _BoolAlias | None = None) -> None:
        assert a is True


def test_pk_opt_bool_def_none_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: _BoolAlias | None = None) -> None:
        assert a is False


def test_pk_opt_bool_def_false(run: Run) -> None:
    @run()
    def _(a: _BoolAlias | None = False) -> None:
        assert a is False


def test_pk_opt_bool_def_false_arg_true(run: Run) -> None:
    @run('-a')
    def _(a: _BoolAlias | None = False) -> None:
        assert a is True


def test_pk_opt_bool_def_true(run: Run) -> None:
    @run()
    def _(a: _BoolAlias | None = True) -> None:
        assert a is True


def test_pk_opt_bool_def_true_arg_false(run: Run) -> None:
    @run('-A')
    def _(a: _BoolAlias | None = True) -> None:
        assert a is False


type _StrAlias = str


def test_p_str(run: Run) -> None:
    val = 'b'

    @run(val)
    def _(a: _StrAlias) -> None:
        assert a == val


def test_p_opt_str(run: Run) -> None:
    @run()
    def _(a: _StrAlias | None) -> None:
        assert a is None


def test_p_opt_str_val(run: Run) -> None:
    val = 'b'

    @run('-a', val)
    def _(a: _StrAlias | None) -> None:
        assert a == val


def test_pk_str_def_str(run: Run) -> None:
    val = 'b'

    @run()
    def _(a: _StrAlias = val) -> None:
        assert a == val


def test_pk_str_def_str_arg_str(run: Run) -> None:
    val = 'c'

    @run('-a', val)
    def _(a: _StrAlias = 'b') -> None:
        assert a == val


def test_pk_opt_str_def_none(run: Run) -> None:
    @run()
    def _(a: _StrAlias | None = None) -> None:
        assert a is None


def test_pk_opt_str_def_none_arg_str(run: Run) -> None:
    val = 'b'

    @run('-a', val)
    def _(a: _StrAlias | None = None) -> None:
        assert a == val


def test_pk_opt_str_def_str(run: Run) -> None:
    val = 'b'

    @run()
    def _(a: _StrAlias | None = val) -> None:
        assert a == val


def test_pk_opt_str_def_str_arg_str(run: Run) -> None:
    val = 'c'

    @run('-a', val)
    def _(a: _StrAlias | None = 'b') -> None:
        assert a == val


def test_var_str(run: Run) -> None:
    val = ('a', 'b', 'c')

    @run(*val)
    def _(*a: _StrAlias) -> None:
        assert a == val


type _IntAlias = int


def test_p_int(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: _IntAlias) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_int(run: Run) -> None:
    val = 2

    @run('-a', val)
    def _(a: _IntAlias = 1) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: _IntAlias = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int(run: Run) -> None:
    @run()
    def _(a: _IntAlias | None) -> None:
        assert a is None


def test_pk_opt_int_arg_int(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: _IntAlias | None) -> None:
        assert a == val


def test_pk_opt_int_def_none(run: Run) -> None:
    @run()
    def _(a: _IntAlias | None = None) -> None:
        assert a is None


def test_pk_opt_int_def_none_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: _IntAlias | None = None) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: _IntAlias | None = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_opt_int_def_int_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: _IntAlias | None = 2) -> None:
        assert isinstance(a, int)
        assert a == val


type _FloatAlias = float


def test_p_float(run: Run) -> None:
    val = 1.0

    @run(val)
    def _(a: _FloatAlias) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_float_def_float(run: Run) -> None:
    val = 1.0

    @run()
    def _(a: _FloatAlias = val) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_float_def_float_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: _FloatAlias = 2.0) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_none(run: Run) -> None:
    @run()
    def _(a: _FloatAlias | None = None) -> None:
        assert a is None


def test_pk_opt_float_def_none_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: _FloatAlias | None = None) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_float(run: Run) -> None:
    val = 1.0

    @run()
    def _(a: _FloatAlias | None = val) -> None:
        assert isinstance(a, float)
        assert a == val


def test_pk_opt_float_def_float_arg_float(run: Run) -> None:
    val = 1.0

    @run('-a', val)
    def _(a: _FloatAlias | None = 2.0) -> None:
        assert isinstance(a, float)
        assert a == val


type _123 = Literal[1, 2, 3]


def test_p_literal_int(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: _123) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_literal_int_def_int(run: Run) -> None:
    val = 1

    @run()
    def _(a: _123 = val) -> None:
        assert isinstance(a, int)
        assert a == val


def test_pk_literal_int_def_int_arg_int(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: _123 = 2) -> None:
        assert isinstance(a, int)
        assert a == val


type _Abc = Literal['a', 'b', 'c']


def test_p_literal_str(run: Run) -> None:
    val = 'a'

    @run(val)
    def _(a: _Abc) -> None:
        assert isinstance(a, str)
        assert a == val


def test_p_literal_str_def_str(run: Run) -> None:
    val = 'a'

    @run()
    def _(a: _Abc = val) -> None:
        assert isinstance(a, str)
        assert a == val


def test_p_literal_str_def_str_arg_str(run: Run) -> None:
    val = 'a'

    @run('-a', val)
    def _(a: _Abc = 'b') -> None:
        assert isinstance(a, str)
        assert a == val


type _PathlibPath = Path


def test_pk_pathlib_path(run: Run) -> None:
    val = Path().absolute()

    @run(str(val))
    def _(p: _PathlibPath) -> None:
        assert isinstance(p, Path)
        assert p == val


def test_pk_opt_pathlib_path_def_none(run: Run) -> None:
    @run()
    def _(p: _PathlibPath | None = None) -> None:
        assert p is None


def test_pk_opt_pathlib_path_def_none_arg_str(run: Run) -> None:
    val = Path().absolute()

    @run('-p', str(val))
    def _(p: _PathlibPath | None = None) -> None:
        assert isinstance(p, Path)
        assert p == val


def test_var_pathlib_path(run: Run) -> None:
    val = (Path('/'), Path('/a'), Path('/a/b'))

    @run(*val)
    def _(*a: _PathlibPath) -> None:
        assert a == val


type _PurePosixPath = PurePosixPath


def test_pk_pathlib_pure_posix_path(run: Run) -> None:
    val = Path().absolute()

    @run(str(val))
    def _(p: _PurePosixPath) -> None:
        assert type(p) is PurePosixPath
        assert p == val


def test_pk_opt_pathlib_pure_posix_path_def_none(run: Run) -> None:
    @run()
    def _(p: _PurePosixPath | None = None) -> None:
        assert p is None


def test_pk_opt_pathlib_pure_posix_path_def_none_arg_str(run: Run) -> None:
    val = Path().absolute()

    @run('-p', str(val))
    def _(p: _PurePosixPath | None = None) -> None:
        assert type(p) is PurePosixPath
        assert p == val


type _TrioPath = trio.Path


def test_var_trio_path(run: Run) -> None:
    val = (trio.Path('/'), trio.Path('/a'), trio.Path('/a/b'))

    @run(*val)
    def _(*a: _TrioPath) -> None:
        assert a == val


class _Foo:
    pass


type _FooAlias = _Foo


def test_raises_unsupported_signature(run: Run) -> None:
    from cleek._parsers import UnsupportedSignature

    def impl(_: _FooAlias) -> None: ...

    with pytest.raises(UnsupportedSignature) as exc_info:
        run()(impl)

    assert exc_info.value.signature == signature(impl, eval_str=True)


def test_po_str(run: Run) -> None:
    val = 'a'

    @run(val)
    def _(a: _Abc, /) -> None:
        assert isinstance(a, str)
        assert a == val


def test_po_str_def_str(run: Run) -> None:
    val = 'a'

    @run()
    def _(a: _Abc = val, /) -> None:
        assert isinstance(a, str)
        assert a == val


type _Recursive = _Recursive | int


def test_infinitely_recursive(run: Run) -> None:
    with pytest.raises(UnsupportedSignature):

        @run()
        def _(a: _Recursive) -> None:
            pass


type _Undefined = Undefined  # pyright: ignore[reportUndefinedVariable]  # noqa: F821


def test_undefined(run: Run) -> None:
    with pytest.raises(UnsupportedSignature):

        @run()
        def _(a: _Undefined) -> None:
            pass


type _Union = int | None


def test_union(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: _Union = None) -> None:
        assert a == val


type _NestedA = int

type _Nested = _NestedA | None


def test_nested(run: Run) -> None:
    val = 1

    @run('-a', val)
    def _(a: _Nested = None) -> None:
        assert a == val


type _B = int

type _A = _B


def test_alias_of_alias(run: Run) -> None:
    val = 1

    @run(val)
    def _(a: _A) -> None:
        assert a == val
