from __future__ import annotations

import shutil
import sys
from pathlib import Path

from .clang_ast import ast_for_entry
from .cli import parse_args
from .compile_commands import selected_entries
from .errors import CodegenError
from .io_utils import load_compile_commands, load_sources
from .paths import resolve_path
from .render import render_header
from .scanner import walk_ast


def run() -> int:
    sys.setrecursionlimit(10000)
    args = parse_args()

    compdb_path = resolve_path(args.compdb, Path.cwd())
    out_dir = resolve_path(args.out_dir, Path.cwd())
    clang_path = args.clang or shutil.which("clang++")
    if clang_path is None:
        raise CodegenError("Unable to find clang++; pass --clang explicitly.")

    compdb = load_compile_commands(compdb_path)
    entries = selected_entries(compdb, args.inputs, compdb_path)

    source_files = {
        resolve_path(entry["file"], resolve_path(entry["directory"], compdb_path.parent))
        for entry in entries
    }
    sources = load_sources(source_files)

    collected = {}
    for entry in entries:
        ast_root = ast_for_entry(entry, clang_path)
        walk_ast(ast_root, [], None, sources, collected)

    types = sorted(
        collected.values(),
        key=lambda item: (str(item.source.file), item.source.line, item.source.col, item.qualified_name),
    )

    output_dir = out_dir / "refl"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "generated.hpp"
    output_path.write_text(render_header(types), encoding="utf-8")
    return 0


def main() -> int:
    try:
        return run()
    except CodegenError as exc:
        print(exc, file=sys.stderr)
        return 1
