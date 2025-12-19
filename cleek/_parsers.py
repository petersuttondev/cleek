from argparse import ArgumentParser
from collections.abc import Callable, Iterable
from enum import Enum, auto, unique
from inspect import Parameter, signature
from pathlib import Path
from typing import (
    Final,
    Literal,
    NamedTuple,
    TYPE_CHECKING,
    _LiteralGenericAlias,  # type: ignore
    cast,
    final,
)

import trio

from ._tasks import Task

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable


@final
class _Options(NamedTuple):
    short: str
    long: str


@final
@unique
class _OptionKind(Enum):
    LOWER = auto()
    UPPWER = auto()


_LOWER: Final = _OptionKind.LOWER

_UPPER: Final = _OptionKind.UPPWER


@final
class _OptionRegistry:
    def __init__(self) -> None:
        self._free_lower_chars: Final = set('abcdefghijklmnopqrstuvwxyz')
        self._free_upper_chars: Final = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self._reserved: Final[set[str]] = set()
        self.reserve(_Options('-h', '--help'))

    def check_free(self, option: str) -> None:
        if option in self._reserved:
            raise ValueError(f'option {option!r} is reserved')

    def _reserve_short(self, option: str) -> None:
        char = option[1]
        self._free_lower_chars.discard(char)
        self._free_upper_chars.discard(char)
        self._reserved.add(option)

    def reserve_short(self, option: str) -> None:
        self.check_free(option)
        self._reserve_short(option)

    def _reserve_long(self, option: str) -> None:
        self._reserved.add(option)

    def reserve_long(self, option: str) -> None:
        self.check_free(option)
        self._reserve_long(option)

    def _reserve(self, options: _Options) -> None:
        self._reserve_short(options.short)
        self._reserve_long(options.long)

    def reserve(self, options: _Options) -> None:
        self.check_free(options.short)
        self.check_free(options.long)
        self._reserve(options)

    def find_free_short(self, kind: _OptionKind, dest: str) -> str:
        match kind:
            case _OptionKind.LOWER:
                candidates = dest.lower()
                free_chars = self._free_lower_chars
            case _OptionKind.UPPWER:
                candidates = dest.upper()
                free_chars = self._free_upper_chars
        for char in candidates:
            if char in free_chars:
                option = f'-{char}'
                if option not in self._reserved:
                    return option
        else:
            raise ValueError(f'cannot find free short option for {dest!r}')

    def find_free_long(self, kind: _OptionKind, dest: str) -> str:
        parts = ['--']
        if kind == _UPPER:
            parts.append('no-')
        parts.append(dest.replace('_', '-'))
        option = ''.join(parts)
        if option in self._reserved:
            raise ValueError(f'cannot find free long option for {dest!r}')
        return option

    def find_free(self, kind: _OptionKind, dest: str) -> _Options:
        return _Options(
            self.find_free_short(kind, dest),
            self.find_free_long(kind, dest),
        )

    def assign(self, kind: _OptionKind, dest: str) -> _Options:
        options = self.find_free(kind, dest)
        self._reserve(options)
        return options

    def assign_lower(self, dest: str) -> _Options:
        return self.assign(_LOWER, dest)

    def assign_upper(self, dest: str) -> _Options:
        return self.assign(_UPPER, dest)


class _Unsupported(ValueError):
    pass


class _UnsupportedDefault(_Unsupported):
    def __init__(self, default: object) -> None:
        self.default: Final = default
        super().__init__(f'unsupported default {default!r}')


@final
class _ArgumentParserBuilder:
    def __init__(self, parser: ArgumentParser) -> None:
        self._parser: Final = parser
        self._add_argument: Final = self._parser.add_argument
        self._options: Final = _OptionRegistry()
        self._assign_lower: Final = self._options.assign_lower
        self._assign_upper: Final = self._options.assign_upper

    # POSITIONAL_OR_KEYWORD #

    # Literal

    def _pk_literal_type_default_empty[T](
        self,
        param: Parameter,
        type: Callable[[str], T],
        choices: Iterable[T],
    ) -> None:
        self._add_argument(param.name, type=type, choices=choices)

    def _pk_literal_type_default_type[T](
        self,
        param: Parameter,
        type: Callable[[str], T],
        choices: Iterable[T],
    ) -> None:
        dest = param.name
        self._add_argument(
            *self._assign_lower(dest),
            default=param.default,
            type=type,
            choices=choices,
            help='default: %(default)s',
            dest=dest,
        )

    def _pk_literal_type[T](
        self,
        param: Parameter,
        type: type[T],
        choices: Iterable[T],
    ) -> None:
        default = param.default
        if default == param.empty:
            self._pk_literal_type_default_empty(param, type, choices)
        elif isinstance(default, type):
            self._pk_literal_type_default_type(param, type, choices)
        else:
            raise _UnsupportedDefault(default)

    def _pk_literal_int(self, param: Parameter, choices: Iterable[int]) -> None:
        self._pk_literal_type(param, int, choices)

    def _pk_literal_str(self, param: Parameter, choices: Iterable[str]) -> None:
        self._pk_literal_type(param, str, choices)

    def _pk_literal(
        self,
        param: Parameter,
        annotation: _LiteralGenericAlias,
    ) -> None:
        def try_as[T](type: type[T]) -> Iterable[T] | None:
            args = annotation.__args__
            return (
                cast(Iterable[T], args)
                if all(isinstance(arg, type) for arg in args)
                else None
            )

        if (args := try_as(int)) is not None:
            self._pk_literal_int(param, args)
        elif (args := try_as(str)) is not None:
            self._pk_literal_str(param, args)
        else:
            raise _Unsupported('unsupported literal')

    # bool #

    def _pk_bool_default(
        self,
        param: Parameter,
        kind: _OptionKind,
        action: Literal['store_true', 'store_false'],
    ) -> None:
        dest = param.name
        self._add_argument(
            *self._options.assign(kind, dest),
            action=action,
            dest=dest,
        )

    def _pk_bool_default_false(self, param: Parameter) -> None:
        self._pk_bool_default(param, _LOWER, 'store_true')

    def _pk_bool_default_true(self, param: Parameter) -> None:
        self._pk_bool_default(param, _UPPER, 'store_false')

    def _pk_bool(self, param: Parameter) -> None:
        default = param.default
        if default is False:
            self._pk_bool_default_false(param)
        elif default is True:
            self._pk_bool_default_true(param)
        else:
            raise _UnsupportedDefault(default)

    def _pk_optional_bool_default_none(self, param: Parameter) -> None:
        options = self._options
        dest = param.name
        pos = options.find_free(_LOWER, dest)
        neg = options.find_free(_UPPER, dest)
        options.reserve(pos)
        options.reserve(neg)
        self._add_argument(*pos, action='store_true', default=None, dest=dest)
        self._add_argument(*neg, action='store_false', dest=dest)

    def _pk_optional_bool(self, param: Parameter) -> None:
        default = param.default
        if default is None:
            self._pk_optional_bool_default_none(param)
        elif default is False:
            self._pk_bool_default_false(param)
        elif default is True:
            self._pk_bool_default_true(param)
        else:
            raise _UnsupportedDefault(default)

    # float #

    def _pk_float_default_float(self, param: Parameter) -> None:
        dest = param.name
        self._add_argument(
            *self._assign_lower(dest),
            type=float,
            default=param.default,
            help='default: %(default)s',
            dest=dest,
        )

    def _pk_float_default_empty(self, param: Parameter) -> None:
        self._add_argument(param.name, type=float)

    def _pk_float(self, param: Parameter) -> None:
        default = param.default
        if default == param.empty:
            self._pk_float_default_empty(param)
        elif isinstance(default, float):
            self._pk_float_default_float(param)
        else:
            raise _UnsupportedDefault(default)

    def _pk_optional_float(self, param: Parameter) -> None:
        dest = param.name
        default = None if param.default == param.empty else param.default
        self._add_argument(
            *self._assign_lower(dest),
            type=float,
            default=default,
            help=None if default is None else 'default: %(default)s',
            dest=dest,
        )

    # int #

    def _pk_int_default_empty(self, param: Parameter) -> None:
        self._add_argument(param.name, type=int)

    def _pk_int_default_int(self, param: Parameter) -> None:
        dest = param.name
        self._add_argument(
            *self._options.assign_lower(dest),
            type=int,
            default=param.default,
            help='default: %(default)s',
            dest=dest,
        )

    def _pk_int(self, param: Parameter) -> None:
        default = param.default
        if default == param.empty:
            self._pk_int_default_empty(param)
        elif isinstance(default, int):
            self._pk_int_default_int(param)
        else:
            raise _UnsupportedDefault(default)

    def _pk_optional_int(self, param: Parameter) -> None:
        dest = param.name
        default = None if param.default == param.empty else param.default
        self._add_argument(
            *self._assign_lower(dest),
            type=int,
            default=param.default,
            help=None if default is None else 'default: %(default)s',
            dest=dest,
        )

    # str #

    def _pk_str_default_str(self, param: Parameter) -> None:
        dest = param.name
        self._add_argument(
            *self._options.assign_lower(dest),
            default=param.default,
            help='default: %(default)s',
            dest=dest,
        )

    def _pk_str_default_empty(self, param: Parameter) -> None:
        self._add_argument(param.name)

    def _pk_str(self, param: Parameter) -> None:
        default = param.default
        if isinstance(default, str):
            self._pk_str_default_str(param)
        elif default == param.empty:
            self._pk_str_default_empty(param)
        else:
            raise _UnsupportedDefault(default)

    def _pk_optional_str_default_str(self, param: Parameter) -> None:
        dest = param.name
        self._add_argument(
            *self._assign_lower(dest),
            default=param.default,
            help='default: %(default)s',
            dest=dest,
        )

    def _pk_optional_str_default_none(self, param: Parameter) -> None:
        dest = param.name
        self._add_argument(*self._options.assign_lower(dest), dest=dest)

    def _pk_optional_str_default_empty(self, param: Parameter) -> None:
        self._pk_optional_str_default_none(param)

    def _pk_optional_str(self, param: Parameter) -> None:
        default = param.default
        if isinstance(default, str):
            self._pk_optional_str_default_str(param)
        elif default is None:
            self._pk_optional_str_default_none(param)
        elif default == param.empty:
            self._pk_optional_str_default_empty(param)
        else:
            raise _UnsupportedDefault(default)

    # - #

    def _pk(self, param: Parameter) -> None:
        annotation = param.annotation
        if isinstance(annotation, _LiteralGenericAlias):
            self._pk_literal(param, annotation)
        elif annotation is bool:
            self._pk_bool(param)
        elif annotation == bool | None:
            self._pk_optional_bool(param)
        elif annotation is float:
            self._pk_float(param)
        elif annotation == float | None:
            self._pk_optional_float(param)
        elif annotation is int:
            self._pk_int(param)
        elif annotation == int | None:
            self._pk_optional_int(param)
        elif annotation is str:
            self._pk_str(param)
        elif annotation == str | None:
            self._pk_optional_str(param)
        else:
            raise _Unsupported(f'unsupported annotation {annotation!r}')

    # VAR_POSITIONAL #

    def _vp_type(self, param: Parameter, type: Callable[[str], object]) -> None:
        self._add_argument(param.name, nargs='*', type=type)

    def _vp_path(self, param: Parameter) -> None:
        self._vp_type(param, Path)

    def _vp_str(self, param: Parameter) -> None:
        self._vp_type(param, str)

    def _vp_trio_path(self, param: Parameter) -> None:
        self._vp_type(param, trio.Path)

    def _vp(self, param: Parameter) -> None:
        annotation = param.annotation
        if annotation is Path:
            self._vp_path(param)
        elif annotation is str:
            self._vp_str(param)
        elif annotation is trio.Path:
            self._vp_trio_path(param)
        else:
            raise _Unsupported(f'unsupported annotation {annotation!r}')

    # -- #

    def _add_param(self, param: Parameter) -> None:
        match param.kind:
            case param.POSITIONAL_OR_KEYWORD:
                self._pk(param)
            case param.VAR_POSITIONAL:
                self._vp(param)
            case _ as kind:
                raise _Unsupported(f'unsupported kind {kind!r}')

    def build(self, obj: '_IntrospectableCallable') -> None:
        sig = signature(obj)
        try:
            for param in sig.parameters.values():
                self._add_param(param)
        except _Unsupported as error:
            import sys
            import traceback
            from rich import print
            from rich.panel import Panel

            print(traceback.format_exc(), file=sys.stderr)

            print(
                Panel(
                    f"Your task function is not supported yet. [u][link=https://github.com/petersuttondev/cleek/issues]Create an issue on GitHub[/link][/u] containing the function siguature below and I'll add support:\n\n{sig}\n",
                    title=':warning: Unsupported Task Function :warning:',
                ),
                file=sys.stderr,
            )

            raise SystemExit(1) from error


def make_parser(task: Task) -> ArgumentParser:
    parser = ArgumentParser(prog=f'clk {task.full_name}')
    builder = _ArgumentParserBuilder(parser)
    builder.build(task.impl)
    return parser
