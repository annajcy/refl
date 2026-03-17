from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate refl::TypeInfo<T> specializations from clang AST."
    )
    parser.add_argument("--compdb", required=True, help="Path to compile_commands.json")
    parser.add_argument("--out-dir", required=True, help="Directory that will receive refl/generated.hpp")
    parser.add_argument("--clang", default=None, help="Path to clang++ used for AST dumping")
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=None,
        help="Optional subset of translation units to scan",
    )
    return parser.parse_args()
