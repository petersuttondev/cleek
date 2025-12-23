# PYTHON_ARGCOMPLETE_OK
from __future__ import annotations
import sys
from typing import TYPE_CHECKING

from cleek._parsers import make_single_parser

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final
    from types import ModuleType, TracebackType

    from cleek._tasks import Task


def try_import(path: 'Path') -> 'ModuleType | None':
    import importlib.util
    import sys

    if not path.exists():
        return
    module_name = 'cleeks'
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_tasks() -> 'ModuleType':
    import os
    from pathlib import Path

    root_path = os.environ.get('CLEEKS_PATH')
    if root_path is not None:
        root_path = Path(root_path).resolve(strict=True)
        cleeks = try_import(root_path) or try_import(root_path / '__init__.py')
        if cleeks is None:
            raise FileNotFoundError('Cannot find cleeks')
        return cleeks
    parent_path = Path().resolve(strict=True)
    root_path = Path('/')
    while True:
        cleeks = try_import(parent_path / 'cleeks.py') or try_import(
            parent_path / 'cleeks/__init__.py'
        )
        if cleeks is not None:
            return cleeks
        parent_path = parent_path.parent
        if parent_path == root_path:
            raise FileNotFoundError('Cannot find cleeks')


def print_tasks(tasks: 'dict[str, Task]') -> None:
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table()
    table.add_column('Task')
    table.add_column('Usage')
    for name, task in tasks.items():
        name = task.full_name
        if task.style is not None:
            style = task.style
            name = f'[{style}]{name}[/{style}]'
        parser = make_single_parser(task)
        if sys.version_info >= (3, 14):
            parser.color = False
        usage = ' '.join(parser.format_usage().strip().split()[1:])
        table.add_row(name, usage)
    console.print(table)


_prev_excepthook: 'Final' = sys.excepthook


def _excepthook(
    type: type[BaseException],
    value: BaseException,
    traceback: 'TracebackType',
) -> None:
    _prev_excepthook(type, value, traceback)
    from cleek._parsers import UnsupportedSignature

    if not isinstance(value, UnsupportedSignature):
        return

    from rich import print
    from rich.panel import Panel

    print(
        '\n',
        Panel(
            f"Your task function is not supported yet. [u][link=https://github.com/petersuttondev/cleek/issues]Create an issue on GitHub[/link][/u] containing the function siguature below and I'll add support:\n\n{value.signature}\n",
            title=':warning: Unsupported Task Function :warning:',
        ),
        '\n',
        file=sys.stderr,
    )



def main() -> None:
    import sys

    try:
        load_tasks()
    except FileNotFoundError as error:
        if len(sys.argv) != 2 or sys.argv[1] != '--completion':
            print(error, file=sys.stderr)
        raise SystemExit(1)

    from cleek import _ctx as ctx
    from cleek._parsers import make_parser
    parser = make_parser(ctx)
    ns = parser.parse_args()

    sys.excepthook = _excepthook

    if ns.task is None:
        print_tasks(ctx.tasks)
        raise SystemExit()

    try:
        task = ctx.tasks[ns.task]
    except KeyError as error:
        print(f'No task named {ns.task!r}', file=sys.stderr)
        raise SystemExit(1) from error

    from cleek._parsers import run

    result = run(task, ns)
    if result is not None:
        print(result)


if __name__ == '__main__':
    main()
