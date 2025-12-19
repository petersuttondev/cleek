from dataclasses import dataclass as _dataclass
from typing import Final as _Final, TYPE_CHECKING, final as _final

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable

__all__: _Final = ('Task', 'tasks')


@_final
@_dataclass(frozen=True)
class Task:
    impl: _Final['_IntrospectableCallable']
    name: _Final[str]
    group: _Final[str | None] = None
    style: _Final[str | None] = None

    @property
    def full_name(self) -> str:
        parts: list[str] = []
        if self.group is not None:
            parts.append(self.group)
        parts.append(self.name)
        return '.'.join(parts)


tasks: _Final[dict[str, Task]] = {}
