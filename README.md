![Cleek](.github/logo.png)

**A Simple task runner generates command line interfaces**

Generates command line interfaces from your task function's type hints. For example;

```python
@task
def binary_op(x: int, y: int, op: Literal['add', 'sub'] = 'add') -> None:
    print(x, op, y)
```

... becomes;

```shell
$ clk binary-op -h
usage: clk binary-op [-h] [-o {add,sub}] x y

positional arguments:
  x
  y

options:
  -h, --help          show this help message and exit
  -o, --op {add,sub}  default: add
```

## Install

```shell
$ git clone https://github.com/petersuttondev/cleek.git
$ pip install cleek
```

## Get Started

1. Create a `cleeks.py` file in the root of your project and add tasks

```python
from cleek import task

@task
def greet(name: str) -> None:
    print(f'Hello, {name}!')
```

2. Run `clk` from anywhere inside your project to see your tasks.

```shell
$ clk
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Task  ┃ Usage               ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ greet │ clk greet [-h] name │
└───────┴─────────────────────┘
```

3. Run `clk <task> -h` to print a task's help.

```shell
$ clk greet
usage: clk greet [-h] name

positional arguments:
  name

options:
  -h, --help  show this help message and exit
```

Finally, run a task:

```shell
$ clk greet peter
Hello, Peter!
```

## Supported Parameters

### `bool`

* Keyword `bool` with `False` or `True` default

```python
def foo(a: bool = False): ...
def foo(a: bool = True): ...
```

* Keyword optional `bool` with `False`, `True`, or `None` default

```python
def foo(a: bool | None = False): ...
def foo(a: bool | None = True): ...
def foo(a: bool | None = None): ...
```

### `str`

* Positional `str`

```python
def foo(a: str): ...
```

* Positional optional `str`

```python
def foo(a: str | None): ...
```
 
* Keyword `str` with `str` default

```python
def foo(a: str = 'a'): ...
```

* Keyword optional `str` with `str` or `None` default

```python
def foo(a: str | None = 'a'): ...
def foo(a: str | None = None): ...
```

* Variadic positional `str`

```python
def foo(*a: str): ...
```

### `int`

* Positional `int`

```python
def foo(a: int): ...
```

* Keyword `int` with `int` default

```python
def foo(a: int = 1): ...
```

* Keyword optional `int` with `int` or `None` default

```python
def foo(a: int | None = 1): ...
def foo(a: int | None = None): ...
```

### `float`

* Positional `float`

```python
def foo(a: float): ...
```

* Keyword `float` with `float` default

```python
def foo(a: float = 1.0): ...
```

* Keyword optional `float` with `float` or `None` default

```python
def foo(a: float | None = 1.0): ...
def foo(a: float | None = None): ...
```

### `Literal[T]`

* Positional `int` literal

```python
@task
def foo(a: Literal[1, 2, 3]) -> None: ...
```

* Positional `str` literal

```python
@task
def foo(a: Literal['a', 'b', 'c']) -> None: ...
```

* Keyword `int` literal with `int` default

```python
@task
def foo(a: Literal[1, 2, 3] = 1) -> None: ...
```

* Keyword `str` literal with `str` default

```python
@task
def foo(a: Literal['a', 'b', 'c'] = 'a') -> None: ...
```

### Misc

* Variadic positional `pathlib.Path`

```python
from pathlib import Path

@task
def foo(*a: Path): ...
```

* Variadic positional `trio.Path`

```python
from trio import Path

@task
def foo(*a: Path): ...
```
