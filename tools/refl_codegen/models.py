from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceLocation:
    file: Path
    line: int
    col: int


@dataclass(frozen=True)
class ReflectedField:
    name: str


@dataclass(frozen=True)
class ReflectedType:
    qualified_name: str
    source: SourceLocation
    fields: tuple[ReflectedField, ...]


@dataclass(frozen=True)
class Ancestor:
    kind: str
    name: str | None
    file: Path | None
