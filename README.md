<p align=center><img src=".github/logo.png" /></p>

<p align=center><b>A simple task runner that generates command line interfaces</b></p>

```Python
from cleek import task

@task
def binary_op(x: int, y: int, op: Literal['add', 'sub'] = 'add') -> None:
    print(x, op, y)
```

<p align=center><b>⬇️ Becomes ⬇️</b></p>

```ShellSession
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

```ShellSession
$ git clone https://github.com/petersuttondev/cleek.git
$ pip install ./cleek
```

## Get Started

1. Create a `cleeks.py` file in the root of your project and add tasks

```Python
from cleek import task

@task
def greet(name: str) -> None:
    print(f'Hello, {name}!')
```

2. Run `clk` from anywhere inside your project to see your tasks.

```ShellSession
$ clk
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Task  ┃ Usage               ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ greet │ clk greet [-h] name │
└───────┴─────────────────────┘
```

3. Run `clk <task> -h` to print a task's help.

```ShellSession
$ clk greet
usage: clk greet [-h] name

positional arguments:
  name

options:
  -h, --help  show this help message and exit
```

Finally, run a task:

```ShellSession
$ clk greet Peter
Hello, Peter!
```

## Supported Parameters

### `bool`

* Keyword `bool` with `False` or `True` default

```Python
def foo(a: bool = False): ...
def foo(a: bool = True): ...
```

* Keyword optional `bool` with `False`, `True`, or `None` default

```Python
def foo(a: bool | None = False): ...
def foo(a: bool | None = True): ...
def foo(a: bool | None = None): ...
```

### `str`

* Positional `str`

```Python
def foo(a: str): ...
```

* Positional optional `str`

```Python
def foo(a: str | None): ...
```
 
* Keyword `str` with `str` default

```Python
def foo(a: str = 'a'): ...
```

* Keyword optional `str` with `str` or `None` default

```Python
def foo(a: str | None = 'a'): ...
def foo(a: str | None = None): ...
```

* Variadic positional `str`

```Python
def foo(*a: str): ...
```

### `int`

* Positional `int`

```Python
def foo(a: int): ...
```

* Keyword `int` with `int` default

```Python
def foo(a: int = 1): ...
```

* Keyword optional `int` with `int` or `None` default

```Python
def foo(a: int | None = 1): ...
def foo(a: int | None = None): ...
```

### `float`

* Positional `float`

```Python
def foo(a: float): ...
```

* Keyword `float` with `float` default

```Python
def foo(a: float = 1.0): ...
```

* Keyword optional `float` with `float` or `None` default

```Python
def foo(a: float | None = 1.0): ...
def foo(a: float | None = None): ...
```

### `Literal[T]`

* Positional `int` literal

```Python
@task
def foo(a: Literal[1, 2, 3]): ...
```

* Positional `str` literal

```Python
@task
def foo(a: Literal['a', 'b', 'c']): ...
```

* Keyword `int` literal with `int` default

```Python
@task
def foo(a: Literal[1, 2, 3] = 1): ...
```

* Keyword `str` literal with `str` default

```Python
@task
def foo(a: Literal['a', 'b', 'c'] = 'a'): ...
```

### Misc

* Variadic positional `pathlib.Path`

```Python
from pathlib import Path

@task
def foo(*a: Path): ...
```

* Variadic positional `trio.Path`

```Python
from trio import Path

@task
def foo(*a: Path): ...
```

## Finding Tasks

1. If the environmental variable `CLEEKS_PATH` is set, `clk` treats the value as a path and attempts to load it. If the load fails, `clk` fails.

2. `clk` searches upwards from the current working directory towards the root directory `/`, looking for a `cleeks.py` script or a `cleeks` package. A script takes precedence over a package if both are found in the same directory.

## Shell Completion

`clk --completion` prints all task names to stdout.

### zsh

```Shell
_complete_clk() {
    reply=($(clk --completion))
}

compctl -K _complete_clk + -f clk
