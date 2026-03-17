from __future__ import annotations

import json
from pathlib import Path


def load_compile_commands(compdb_path: Path) -> list[dict]:
    with compdb_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_sources(paths: set[Path]) -> dict[Path, list[str]]:
    sources: dict[Path, list[str]] = {}
    for path in paths:
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                sources[path] = handle.read().splitlines(keepends=True)
    return sources


def get_source_lines(path: Path, sources: dict[Path, list[str]]) -> list[str] | None:
    if path in sources:
        return sources[path]
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        sources[path] = handle.read().splitlines(keepends=True)
    return sources[path]
