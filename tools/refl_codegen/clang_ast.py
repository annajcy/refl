from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

from .errors import CodegenError
from .paths import resolve_path


def sanitize_arguments(arguments: list[str], source_file: Path, working_directory: Path, clang_path: str) -> list[str]:
    sanitized = [clang_path]
    skip_next = False
    for arg in arguments[1:]:
        if skip_next:
            skip_next = False
            continue

        if arg in {"-c", "/c"}:
            continue
        if arg in {"-o", "-MF", "-MT", "-MQ", "--serialize-diagnostics", "-MJ"}:
            skip_next = True
            continue
        if arg in {"-MD", "-MMD", "-MP"}:
            continue
        if arg.startswith("-o") and arg != "-Winvalid-offsetof":
            continue
        if arg.startswith("/Fo"):
            continue
        if arg.startswith("-DREFL_USE_GENERATED"):
            continue

        candidate = Path(arg)
        if candidate.suffix in {".cpp", ".cc", ".cxx", ".c", ".mm"}:
            resolved = resolve_path(arg, working_directory)
            if resolved == source_file:
                continue

        sanitized.append(arg)

    sanitized.extend(["-Xclang", "-ast-dump=json", "-fsyntax-only", str(source_file)])
    return sanitized


def ast_for_entry(entry: dict, clang_path: str) -> dict:
    directory = resolve_path(entry["directory"], Path.cwd())
    source_file = resolve_path(entry["file"], directory)

    if "arguments" in entry:
        arguments = list(entry["arguments"])
    else:
        command = entry["command"]
        arguments = shlex.split(command, posix=os.name != "nt")

    ast_command = sanitize_arguments(arguments, source_file, directory, clang_path)
    completed = subprocess.run(
        ast_command,
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CodegenError(
            "\n".join(
                [
                    f"{source_file}: clang AST dump failed",
                    "Command:",
                    " ".join(ast_command),
                    "stderr:",
                    completed.stderr.strip() or "<empty>",
                ]
            )
        )

    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise CodegenError(f"{source_file}: failed to parse clang AST JSON: {exc}") from exc
