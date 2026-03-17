from __future__ import annotations

from pathlib import Path

from .errors import CodegenError
from .paths import resolve_path


def selected_entries(compdb: list[dict], requested_inputs: list[str] | None, compdb_path: Path) -> list[dict]:
    directory = compdb_path.parent
    by_file: dict[Path, dict] = {}
    for entry in compdb:
        source = resolve_path(entry["file"], resolve_path(entry["directory"], directory))
        by_file[source] = entry

    if requested_inputs is None:
        return list(by_file.values())

    selected: list[dict] = []
    missing: list[str] = []
    for item in requested_inputs:
        source = resolve_path(item, Path.cwd())
        entry = by_file.get(source)
        if entry is None:
            missing.append(str(source))
            continue
        selected.append(entry)

    if missing:
        available = "\n".join(f"  - {path}" for path in sorted(str(path) for path in by_file))
        raise CodegenError(
            "No compile_commands entry found for:\n"
            + "\n".join(f"  - {path}" for path in missing)
            + "\nAvailable inputs:\n"
            + available
        )
    return selected
