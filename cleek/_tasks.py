from dataclasses import dataclass as _dataclass
from typing import Final as _Final, TYPE_CHECKING, final as _final

if TYPE_CHECKING:
    from inspect import _IntrospectableCallable

__all__: _Final = ('Task',)


@_final
@_dataclass(frozen=True)
class Task:
    impl: _IntrospectableCallable
    name: str
    group: str | None
    style: str | None

    @property
    def doc(self) -> str | None:
        return self.impl.__doc__

    @property
    def full_name(self) -> str:
        parts: list[str] = []
        if self.group is not None:
            parts.append(self.group)
        parts.append(self.name)
        return '.'.join(parts)
