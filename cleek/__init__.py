from typing import Final as _Final

from cleek._tasks import Context as _Context

__all__ = ('customize', 'task')

_ctx: _Final = _Context()
customize: _Final = _ctx.customize
task: _Final = _ctx.task
