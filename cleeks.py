from pathlib import Path
from typing import Literal

import trio
from cleek import customize, task


@task
def none() -> None:
    pass


literal_task = customize(style='green')


@literal_task
def positional_literal_int(a: Literal[1, 2, 3]) -> None:
    print(type(a), a)


@literal_task
def positional_literal_str(a: Literal['a', 'b', 'c']) -> None:
    print(type(a), a)


@literal_task
def keyword_literal_int(a: Literal[1, 2, 3] = 1) -> None:
    print(type(a), a)


@literal_task
def keyword_literal_str(a: Literal['a', 'b', 'c'] = 'a') -> None:
    print(type(a), a)


bool_task = customize(style='red')


@bool_task
def keyword_bool_default_false(a: bool = False) -> None:
    print(type(a), a)


@bool_task
def keyword_bool_default_true(a: bool = True) -> None:
    print(type(a), a)


@bool_task
def keyword_optional_bool_default_none(a: bool | None = None) -> None:
    print(type(a), a)


@bool_task
def keyword_optional_bool_default_false(a: bool | None = False) -> None:
    print(type(a), a)


@bool_task
def keyword_optional_bool_default_true(a: bool | None = True) -> None:
    print(type(a), a)


float_task = customize(style='yellow')


@float_task
def positional_float(a: float) -> None:
    print(type(a), a)


@float_task
def keyword_float_default_float(a: float = 1.0) -> None:
    print(type(a), a)


@float_task
def optional_positional_optional_float(a: float | None) -> None:
    print(type(a), a)


str_task = customize(style='blue')


@str_task
def positional_str(a: str) -> None:
    print(type(a), a)


@str_task
def positional_optional_str(a: str | None) -> None:
    print(type(a), a)


@str_task
def keyword_str_default_str(a: str = 'a') -> None:
    print(type(a), a)


@str_task
def keyword_optional_str_default_str(a: str | None = 'a') -> None:
    print(type(a), a)


@str_task
def keyword_optional_str_default_none(a: str | None = None) -> None:
    print(type(a), a)


@str_task
def vardic_positional_str(*a: str) -> None:
    print(type(a), a)


path_task = customize(style='purple')


@path_task
def vardic_positional_path(*a: Path) -> None:
    print(type(a), a)


@path_task
def vardic_positional_trio_path(*a: trio.Path) -> None:
    print(type(a), a)


multi_task = customize(style='cyan')


@multi_task
def multi_1(a: str, b: str = 'b') -> None:
    print(type(a), a)
    print(type(b), b)


@multi_task
def multi_2(
    a: int = 1,
    b: str = 'b',
    c: Literal['c1', 'c2', 'c3'] = 'c1',
    d: bool | None = None,
    az: bool | None = False,
) -> None:
    print(type(a), a)
    print(type(b), b)
    print(type(c), c)
    print(type(d), d)
    print(type(az), az)


async_task = customize(style='orange')


@task
async def async_1(a: float) -> None:
    print(f'Sleeping for {a} seconds')
    await trio.sleep(1)
