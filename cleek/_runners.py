from collections.abc import Sequence
from inspect import iscoroutine, iscoroutinefunction, signature
from cleek._parsers import make_parser
from cleek._tasks import Task


def run(task: Task, task_args: Sequence[str]):
    parser = make_parser(task)
    ns = parser.parse_args(task_args)
    args = []
    for param in signature(task.impl).parameters.values():
        value = getattr(ns, param.name)
        if param.kind == param.VAR_POSITIONAL:
            args.extend(value)
        else:
            args.append(value)

    if iscoroutinefunction(task.impl):
        from functools import partial
        import trio

        return trio.run(partial(task.impl, *args))

    result = task.impl(*args)

    if iscoroutine(result):

        async def run_result():
            return await result

        import trio

        return trio.run(run_result)

    return result

