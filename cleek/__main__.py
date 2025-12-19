from inspect import iscoroutine, iscoroutinefunction, signature
from typing import TYPE_CHECKING, Sequence

from cleek._parsers import make_parser
from cleek._tasks import Task


if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType


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


def print_tasks(tasks: dict[str, Task]) -> None:
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
        parser = make_parser(task)
        parser.color = False
        usage = ' '.join(parser.format_usage().strip().split()[1:])
        table.add_row(name, usage)
    console.print(table)


def main() -> None:
    import sys

    try:
        load_tasks()
    except FileNotFoundError as error:
        if len(sys.argv) != 2 or sys.argv[1] != '--completion':
            print(error, file=sys.stderr)
        raise SystemExit(1)

    from cleek._tasks import tasks

    from argparse import SUPPRESS, REMAINDER, ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        '--completion',
        action='store_true',
        default=False,
        help=SUPPRESS,
    )
    parser.add_argument('task', nargs='?')
    parser.add_argument('task_args', nargs=REMAINDER)
    ns = parser.parse_args()

    if ns.completion:
        print(*(task.full_name for task in tasks.values()))
        raise SystemExit()

    if ns.task is None:
        print_tasks(tasks)
        raise SystemExit()

    try:
        task = tasks[ns.task]
    except KeyError as error:
        print(f'No task named {ns.task!r}', file=sys.stderr)
        raise SystemExit(1) from error

    from cleek._runners import run

    result = run(task, ns.task_args)
    if result is not None:
        print(result)


if __name__ == '__main__':
    main()
